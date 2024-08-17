import math
import numpy as np

import torch
import torch.nn as nn
from torch.nn import Transformer
from torch import Tensor
from torch.utils.data import DataLoader

#########################################################################################################
# Classes
#########################################################################################################

# helper Module that adds positional encoding to the token embedding to introduce a notion of word order.
class PositionalEncoding(nn.Module):
    def __init__(self, emb_size: int, dropout: float, maxlen: int = 500):
        super(PositionalEncoding, self).__init__()
        # maxlen default og = 5000
        den = torch.exp(- torch.arange(0, emb_size, 2)* math.log(10000) / emb_size)
        pos = torch.arange(0, maxlen).reshape(maxlen, 1)
        pos_embedding = torch.zeros((maxlen, emb_size))
        pos_embedding[:, 0::2] = torch.sin(pos * den)
        pos_embedding[:, 1::2] = torch.cos(pos * den)
        pos_embedding = pos_embedding.unsqueeze(-2)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer('pos_embedding', pos_embedding)

    def forward(self, token_embedding: Tensor):
        return self.dropout(token_embedding + self.pos_embedding[:token_embedding.size(0), :])

# helper Module to convert tensor of input indices into corresponding tensor of token embeddings
class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size: int, emb_size):
        super(TokenEmbedding, self).__init__()
        self.embedding = nn.Embedding(vocab_size, emb_size)
        self.emb_size = emb_size

    def forward(self, tokens: Tensor):
        return self.embedding(tokens.long()) * math.sqrt(self.emb_size)

# Seq2Seq Network
class Seq2SeqTransformer(nn.Module):
    def __init__(self, num_encoder_layers: int, num_decoder_layers: int, emb_size: int, nhead: int, STATE_VOCAB_size: int, MOVE_VOCAB_size: int, dim_feedforward: int = 512, dropout: float = 0.1):
        super(Seq2SeqTransformer, self).__init__()
        self.transformer = Transformer(d_model=emb_size, nhead=nhead, num_encoder_layers=num_encoder_layers, num_decoder_layers=num_decoder_layers, dim_feedforward=dim_feedforward, dropout=dropout)
        self.generator = nn.Linear(emb_size, MOVE_VOCAB_size)
        self.src_tok_emb = TokenEmbedding(STATE_VOCAB_size, emb_size)
        self.tgt_tok_emb = TokenEmbedding(MOVE_VOCAB_size, emb_size)
        self.positional_encoding = PositionalEncoding(emb_size, dropout=dropout)

    def forward(self, src: Tensor, trg: Tensor, src_mask: Tensor, tgt_mask: Tensor):
        src_emb = self.positional_encoding(self.src_tok_emb(src))
        tgt_emb = self.positional_encoding(self.tgt_tok_emb(trg))
        # outs = self.transformer(src_emb, tgt_emb, src_mask, tgt_mask, None, src_padding_mask, tgt_padding_mask, memory_key_padding_mask)
        outs = self.transformer(src_emb, tgt_emb, src_mask, tgt_mask, None, None, None, None)
        return self.generator(outs)

    def encode(self, src: Tensor, src_mask: Tensor):
        return self.transformer.encoder(self.positional_encoding(self.src_tok_emb(src)), src_mask)

    def decode(self, tgt: Tensor, memory: Tensor, tgt_mask: Tensor):
        return self.transformer.decoder(self.positional_encoding(self.tgt_tok_emb(tgt)), memory, tgt_mask)


class DataLoaderWrapper(DataLoader):

    def __init__(self, train_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, DEVICE):
        self.STATE_LANGUAGE = STATE_LANGUAGE
        self.MOVE_LANGUAGE = MOVE_LANGUAGE
        self.text_transform = text_transform
        self.DEVICE = DEVICE
        super().__init__(train_iter, batch_size=BATCH_SIZE, collate_fn=self.collate_fn)

    # converts batched state, move pairs to two inline tensors
    def collate_fn(self, batch):

        # can't put strings in a tensor so have to encode on cpu
        batch = np.asarray(batch)
        state_out = self.text_transform[self.STATE_LANGUAGE].encode_batch(batch[:,0])
        move_out = self.text_transform[self.MOVE_LANGUAGE].encode_batch(batch[:,1])

        state_batch, move_batch = [], []
        state_tokens, move_tokens = len(state_out[0].ids), len(move_out[0].ids)

        for idx in range(len(state_out)):
            state_batch.append(torch.tensor(state_out[idx].ids).reshape(state_tokens, 1))                       
            move_batch.append(torch.tensor(move_out[idx].ids).reshape(move_tokens, 1))

        state_batch = torch.cat(state_batch, dim=1).to(self.DEVICE)
        move_batch = torch.cat(move_batch, dim=1).to(self.DEVICE)

        return state_batch, move_batch

#########################################################################################################
# Functions
#########################################################################################################

# not sure how this works or what it does
def generate_square_subsequent_mask(sz, DEVICE):
    mask = (torch.triu(torch.ones((sz, sz), device=DEVICE)) == 1).transpose(0, 1)
    mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
    return mask


def construct_text_transform(state_tokenizer, move_tokenizer, STATE_LANGUAGE, MOVE_LANGUAGE):

    # ``src`` and ``tgt`` language text transforms to convert raw strings into tensors indices
    text_transform = {}
    text_transform[STATE_LANGUAGE] = state_tokenizer
    text_transform[MOVE_LANGUAGE] = move_tokenizer
    return text_transform

def create_mask(src, tgt, DEVICE):
    src_seq_len = src.shape[0]
    tgt_seq_len = tgt.shape[0]

    tgt_mask = generate_square_subsequent_mask(tgt_seq_len, DEVICE)
    src_mask = torch.zeros((src_seq_len, src_seq_len),device=DEVICE).type(torch.bool)
    return src_mask, tgt_mask

def train_epoch(model, optimizer, loss_fn, train_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, DEVICE):

    model.train()

    losses = 0
    train_dataloader = DataLoaderWrapper(train_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, DEVICE)

    for src, tgt in train_dataloader:
        tgt_input = tgt[:-1, :]
        src_mask, tgt_mask = create_mask(src, tgt_input, DEVICE)
        logits = model(src, tgt_input, src_mask, tgt_mask)
        optimizer.zero_grad()

        tgt_out = tgt[1:, :]
        loss = loss_fn(logits.reshape(-1, logits.shape[-1]), tgt_out.reshape(-1))
        loss.backward()

        optimizer.step()
        losses += loss.item()

    return losses / len(list(train_dataloader))

def evaluate(model, loss_fn, val_iter, BATCH_SIZE, DEVICE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE):
    model.eval().to(DEVICE)
    losses = 0
    val_dataloader = DataLoaderWrapper(val_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, DEVICE)

    for src, tgt in val_dataloader:
        tgt_input = tgt[:-1, :]
        src_mask, tgt_mask = create_mask(src, tgt_input, DEVICE)
        logits = model(src, tgt_input, src_mask, tgt_mask)

        tgt_out = tgt[1:, :]
        loss = loss_fn(logits.reshape(-1, logits.shape[-1]), tgt_out.reshape(-1))
        losses += loss.item()

    return losses / len(list(val_dataloader))

def evaluate_hand(model, val_iter, BATCH_SIZE, DEVICE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, BOS_IDX):
    model.eval()

    val_dataloader = DataLoaderWrapper(val_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, DEVICE)

    start_symbol = BOS_IDX
    good = 0
    for src, tgt in val_dataloader:

        # strips EOS marker
        tgt_input = tgt[:-1, :]
        src_mask, tgt_mask = create_mask(src, tgt_input, DEVICE)

        logits = model(src, tgt_input, src_mask, tgt_mask)

        # selected cards followed by the EOS markers
        # this is why the output is twice as long as the batch size.
        # TODO take out the EOS marker prediction from model and loss evaluation

        prob = logits[0,:,:]
        max_prob, next_words = torch.max(prob, dim=1)

        start_sym_vec =  torch.ones(next_words.shape[0], 1).type(torch.int).to(DEVICE)
        start_sym_vec = torch.mul(start_sym_vec, start_symbol)


        next_words = torch.reshape(next_words, (next_words.shape[0], 1))
        next_words = torch.cat((start_sym_vec, next_words), 1)

        selected_cards = text_transform[MOVE_LANGUAGE].decode_batch(next_words.tolist())
        states_list = text_transform[STATE_LANGUAGE].decode_batch(src.transpose(0, 1).tolist())

        for idx in range(len(next_words)):
            player_hand = states_list[idx].split()[0]
            player_hand = player_hand.split("_")
            player_hand = player_hand[2:len(player_hand)]

            card_val = selected_cards[idx].split("_")[2]
            if card_val in player_hand:
                good += 1

    return good / len(val_iter)
