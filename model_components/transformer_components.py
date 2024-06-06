import math
import torch
import torch.nn as nn

from torch.nn import Transformer
from torch import Tensor
from torch.utils.data import DataLoader
from torch.nn.utils.rnn import pad_sequence

from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator

from typing import Iterable, List

#########################################################################################################
# Classes
#########################################################################################################

# helper Module that adds positional encoding to the token embedding to introduce a notion of word order.
class PositionalEncoding(nn.Module):
    def __init__(self, emb_size: int, dropout: float, maxlen: int = 5000):
        super(PositionalEncoding, self).__init__()
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

    def forward(self, src: Tensor, trg: Tensor, src_mask: Tensor, tgt_mask: Tensor, src_padding_mask: Tensor, tgt_padding_mask: Tensor, memory_key_padding_mask: Tensor):
        src_emb = self.positional_encoding(self.src_tok_emb(src))
        tgt_emb = self.positional_encoding(self.tgt_tok_emb(trg))
        outs = self.transformer(src_emb, tgt_emb, src_mask, tgt_mask, None, src_padding_mask, tgt_padding_mask, memory_key_padding_mask)
        return self.generator(outs)

    def encode(self, src: Tensor, src_mask: Tensor):
        return self.transformer.encoder(self.positional_encoding(self.src_tok_emb(src)), src_mask)

    def decode(self, tgt: Tensor, memory: Tensor, tgt_mask: Tensor):
        return self.transformer.decoder(self.positional_encoding(self.tgt_tok_emb(tgt)), memory, tgt_mask)

class DataLoaderWrapper(DataLoader):

    def __init__(self, train_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, PAD_IDX):
        self.STATE_LANGUAGE = STATE_LANGUAGE
        self.MOVE_LANGUAGE = MOVE_LANGUAGE
        self.PAD_IDX = PAD_IDX
        self.text_transform = text_transform
        super().__init__(train_iter, batch_size=BATCH_SIZE, collate_fn=self.collate_fn)

    # function to collate data samples into batch tensors
    def collate_fn(self, batch):
        src_batch, tgt_batch = [], []
        for src_sample, tgt_sample in batch:
            src_batch.append(self.text_transform[self.STATE_LANGUAGE](src_sample.rstrip("\n")))
            tgt_batch.append(self.text_transform[self.MOVE_LANGUAGE](tgt_sample.rstrip("\n")))

        src_batch = pad_sequence(src_batch, padding_value=self.PAD_IDX)
        tgt_batch = pad_sequence(tgt_batch, padding_value=self.PAD_IDX)
        return src_batch, tgt_batch

class SeqTransforms():

    def __init__(self, token_transform, vocab_transform, BOS_IDX, EOS_IDX):
        self.BOS_IDX = BOS_IDX
        self.EOS_IDX = EOS_IDX
        self.token_transform = token_transform
        self.vocab_transform = vocab_transform

    def seqtrans(self, ln):
        return self.sequential_transforms(self.token_transform[ln], #Tokenization
                                          self.vocab_transform[ln], #Numericalization
                                          self.tensor_transform) # Add BOS/EOS and create tensor

    # helper function to club together sequential operations
    def sequential_transforms(self, *transforms):
        def func(txt_input):
            for transform in transforms:
                txt_input = transform(txt_input)
            return txt_input
        return func

    # function to add BOS/EOS and create tensor for input sequence indices
    def tensor_transform(self, token_ids: List[int]):
        return torch.cat((torch.tensor([self.BOS_IDX]),
                        torch.tensor(token_ids),
                        torch.tensor([self.EOS_IDX])))

#########################################################################################################
# Functions
#########################################################################################################
# not sure how this works or what it does
def generate_square_subsequent_mask(sz, DEVICE):
    mask = (torch.triu(torch.ones((sz, sz), device=DEVICE)) == 1).transpose(0, 1)
    mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
    return mask

def construct_token_transform(STATE_LANGUAGE, MOVE_LANGUAGE):
    token_transform = {}
    token_transform[STATE_LANGUAGE] = get_tokenizer(None)
    token_transform[MOVE_LANGUAGE] = get_tokenizer(None)
    return token_transform

def construct_vocab_transform(train_iter, STATE_LANGUAGE, MOVE_LANGUAGE, UNK_IDX, special_symbols, token_transform):
    vocab_transform = {}
    for ln in [STATE_LANGUAGE, MOVE_LANGUAGE]:
        # Training data Iterator
        yield_out = yield_tokens(train_iter, "state", STATE_LANGUAGE, MOVE_LANGUAGE, token_transform)   

        # Create torchtext's Vocab object
        vocab_transform[ln] = build_vocab_from_iterator(yield_tokens(train_iter, ln, STATE_LANGUAGE, MOVE_LANGUAGE, token_transform), min_freq=1, specials=special_symbols, special_first=True)

    # Set ``UNK_IDX`` as the default index. This index is returned when the token is not found.
    # If not set, it throws ``RuntimeError`` when the queried token is not found in the Vocabulary.
    for ln in [STATE_LANGUAGE, MOVE_LANGUAGE]:
        vocab_transform[ln].set_default_index(UNK_IDX)

    return vocab_transform

def construct_text_transform(token_transform, vocab_transform, STATE_LANGUAGE, MOVE_LANGUAGE, BOS_IDX, EOS_IDX):

    seqtrans = SeqTransforms(token_transform, vocab_transform, BOS_IDX, EOS_IDX)

    # ``src`` and ``tgt`` language text transforms to convert raw strings into tensors indices
    text_transform = {}
    for ln in [STATE_LANGUAGE, MOVE_LANGUAGE]:
        text_transform[ln] = seqtrans.seqtrans(ln)

    return text_transform


# helper function to yield list of tokens
def yield_tokens(data_iter: Iterable, language: str, STATE_LANGUAGE: str, MOVE_LANGUAGE: str, token_transform) -> List[str]:
    language_index = {STATE_LANGUAGE: 0, MOVE_LANGUAGE: 1}
    for data_sample in data_iter:
        yield token_transform[language](data_sample[language_index[language]])

def create_mask(src, tgt, DEVICE, PAD_IDX):
    src_seq_len = src.shape[0]
    tgt_seq_len = tgt.shape[0]

    tgt_mask = generate_square_subsequent_mask(tgt_seq_len, DEVICE)
    src_mask = torch.zeros((src_seq_len, src_seq_len),device=DEVICE).type(torch.bool)
    src_padding_mask = (src == PAD_IDX).transpose(0, 1)
    tgt_padding_mask = (tgt == PAD_IDX).transpose(0, 1)
    return src_mask, tgt_mask, src_padding_mask, tgt_padding_mask

def train_epoch(model, optimizer, loss_fn, train_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, PAD_IDX, DEVICE):
    model.train()
    losses = 0
    train_dataloader = DataLoaderWrapper(train_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, PAD_IDX)

    for src, tgt in train_dataloader:
        src = src.to(DEVICE)
        tgt = tgt.to(DEVICE)

        tgt_input = tgt[:-1, :]
        src_mask, tgt_mask, src_padding_mask, tgt_padding_mask = create_mask(src, tgt_input, DEVICE, PAD_IDX)
        logits = model(src, tgt_input, src_mask, tgt_mask,src_padding_mask, tgt_padding_mask, src_padding_mask)
        optimizer.zero_grad()

        tgt_out = tgt[1:, :]
        loss = loss_fn(logits.reshape(-1, logits.shape[-1]), tgt_out.reshape(-1))
        loss.backward()

        optimizer.step()
        losses += loss.item()

    return losses / len(list(train_dataloader))

def evaluate(model, loss_fn, val_iter, BATCH_SIZE, DEVICE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, PAD_IDX):
    model.eval()
    losses = 0
    val_dataloader = DataLoaderWrapper(val_iter, BATCH_SIZE, text_transform, STATE_LANGUAGE, MOVE_LANGUAGE, PAD_IDX)

    for src, tgt in val_dataloader:
        src = src.to(DEVICE)
        tgt = tgt.to(DEVICE)

        tgt_input = tgt[:-1, :]
        src_mask, tgt_mask, src_padding_mask, tgt_padding_mask = create_mask(src, tgt_input, DEVICE, PAD_IDX)
        logits = model(src, tgt_input, src_mask, tgt_mask,src_padding_mask, tgt_padding_mask, src_padding_mask)

        tgt_out = tgt[1:, :]
        loss = loss_fn(logits.reshape(-1, logits.shape[-1]), tgt_out.reshape(-1))
        losses += loss.item()

    return losses / len(list(val_dataloader))
