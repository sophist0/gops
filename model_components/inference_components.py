import torch

from model_components.transformer_components import generate_square_subsequent_mask

def random_decode(model, src, src_mask, max_len, start_symbol, DEVICE, EOS_IDX, k):
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

        top_k_val, top_k_idx = torch.topk(prob, k, dim=1)
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

def translate_random(model: torch.nn.Module, src_sentence: str, text_transform, MOVE_LANGUAGE, STATE_LANGUAGE, BOS_IDX, DEVICE, EOS_IDX, topk):
    model.eval()
    src = text_transform[STATE_LANGUAGE].encode(src_sentence).ids
    src = torch.tensor(src).view(-1, 1)

    num_tokens = src.shape[0]
    src_mask = (torch.zeros(num_tokens, num_tokens)).type(torch.bool)
    tgt_tokens = random_decode(model,  src, src_mask, num_tokens + 5, BOS_IDX, DEVICE, EOS_IDX, topk).flatten()
    decoded_word = text_transform[MOVE_LANGUAGE].decode(tgt_tokens.tolist())
    return decoded_word
