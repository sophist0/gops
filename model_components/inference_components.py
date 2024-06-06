import torch

from model_components.transformer_components import generate_square_subsequent_mask

#########################################################################################################
# TODO: Consolidate the decode and translate functions below
#########################################################################################################

# function to generate output sequence using greedy algorithm
def greedy_decode(model, src, src_mask, max_len, start_symbol, DEVICE, EOS_IDX):
    src = src.to(DEVICE)
    src_mask = src_mask.to(DEVICE)

    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type(torch.long).to(DEVICE)
    for i in range(max_len-1):
        memory = memory.to(DEVICE)
        tgt_mask = (generate_square_subsequent_mask(ys.size(0), DEVICE).type(torch.bool)).to(DEVICE)
        out = model.decode(ys, memory, tgt_mask)
        out = out.transpose(0, 1)
        prob = model.generator(out[:, -1])

        # torch max returns max_val, max_index
        max_prob, next_word = torch.max(prob, dim=1)
        next_word = next_word.item()

        ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=0)
        if next_word == EOS_IDX:
            break
    return ys

# actual function to translate input sentence into target language
def translate_greedy(model: torch.nn.Module, src_sentence: str, text_transform, vocab_transform, MOVE_LANGUAGE, STATE_LANGUAGE, BOS_IDX, DEVICE, EOS_IDX):
    model.eval()
    src = text_transform[STATE_LANGUAGE](src_sentence).view(-1, 1)
    num_tokens = src.shape[0]
    src_mask = (torch.zeros(num_tokens, num_tokens)).type(torch.bool)
    tgt_tokens = greedy_decode(model,  src, src_mask, num_tokens + 5, BOS_IDX, DEVICE, EOS_IDX).flatten()
    return " ".join(vocab_transform[MOVE_LANGUAGE].lookup_tokens(list(tgt_tokens.cpu().numpy()))).replace("<bos>", "").replace("<eos>", "")

def random_decode(model, src, src_mask, max_len, start_symbol, DEVICE, EOS_IDX):
    src = src.to(DEVICE)
    src_mask = src_mask.to(DEVICE)

    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type(torch.long).to(DEVICE)
    for i in range(max_len-1):
        memory = memory.to(DEVICE)
        tgt_mask = (generate_square_subsequent_mask(ys.size(0), DEVICE).type(torch.bool)).to(DEVICE)
        out = model.decode(ys, memory, tgt_mask)
        out = out.transpose(0, 1)
        prob = model.generator(out[:, -1])

        top_k_val, top_k_idx = torch.topk(prob, 5, dim=1)

        # period char is 5, could break on 5 and add a EOS_IDX after that
        if EOS_IDX is top_k_idx[0][0].item():
            ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).fill_(EOS_IDX)], dim=0)
            break
        else:   
            # sort top_k_idx and select one.
            idx_perm = torch.randperm(top_k_idx.size(1))
            rand_next_word = top_k_idx[0][idx_perm[0]]
            rand_next_word = rand_next_word.item()
            ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).fill_(rand_next_word)], dim=0)
    return ys

def translate_random(model: torch.nn.Module, src_sentence: str, text_transform, vocab_transform, MOVE_LANGUAGE, STATE_LANGUAGE, BOS_IDX, DEVICE, EOS_IDX):
    model.eval()
    src = text_transform[STATE_LANGUAGE](src_sentence).view(-1, 1)
    num_tokens = src.shape[0]
    src_mask = (torch.zeros(num_tokens, num_tokens)).type(torch.bool)
    tgt_tokens = random_decode(model,  src, src_mask, num_tokens + 5, BOS_IDX, DEVICE, EOS_IDX).flatten()
    return " ".join(vocab_transform[MOVE_LANGUAGE].lookup_tokens(list(tgt_tokens.cpu().numpy()))).replace("<bos>", "").replace("<eos>", "")
