import logging
import math
import torch
from torch import nn

from dltranz.trx_encoder import PaddedBatch

logger = logging.getLogger(__name__)

try:
    from torch.nn import TransformerEncoder, TransformerEncoderLayer, LayerNorm
except ImportError:
    logger.error('Can not import Transformers')


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :x.size(1)]
        return self.dropout(x)


class TransformerSeqEncoder(nn.Module):
    def __init__(self, input_size, params):
        super().__init__()

        self.shared_layers = params['shared_layers']
        self.n_layers = params['n_layers']
        self.use_after_mask = params['use_after_mask']
        self.use_src_key_padding_mask = params['use_src_key_padding_mask']
        self.use_positional_encoding = params['use_positional_encoding']

        self.starter = torch.nn.Parameter(torch.randn(1, 1, input_size)) if params['train_starter'] else None

        self.enc_layer = TransformerEncoderLayer(
            d_model=input_size,
            nhead=params['n_heads'],
            dim_feedforward=params['dim_hidden'],
            dropout=params['dropout'])

        enc_norm = LayerNorm(input_size)
        self.enc = TransformerEncoder(self.enc_layer, params['n_layers'], enc_norm)
        self.pe = PositionalEncoding(max_len=params['max_seq_len'], d_model=input_size, dropout=params['dropout'])

    @staticmethod
    def generate_square_subsequent_mask(sz):
        r"""Generate a square mask for the sequence. The masked positions are filled with float('-inf').
            Unmasked positions are filled with float(0.0).
        """
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

    def forward(self, x):
        batch_size = x.payload.size()[0]
        seq_len_max = x.payload.size()[1]
        x_t = torch.transpose(x.payload, 0, 1)

        if self.starter is not None:
            x_t = torch.cat([self.starter.expand(1, batch_size, -1), x_t], dim=0)

        if self.use_after_mask:
            mask = self.generate_square_subsequent_mask(x_t.size(0)).to(x_t.device)
        else:
            mask = None

        if self.use_src_key_padding_mask:
            src_key_padding_mask = torch.stack([torch.BoolTensor([False] * l + [True] * (seq_len_max - l))
                                                for l in x.seq_lens]).to(x.payload.device)
        else:
            src_key_padding_mask = None

        if self.use_positional_encoding:
            x_t = self.pe(x_t)

        if not self.shared_layers:
            out = self.enc(x_t, mask=mask, src_key_padding_mask=src_key_padding_mask)
        else:
            out = x_t
            for _ in range(self.n_layers):
                out = self.enc_layer(out, mask=mask, src_key_padding_mask=src_key_padding_mask)

        out = torch.transpose(out, 0, 1)

        return PaddedBatch(out, x.seq_lens)

class CustomTransformerSeqEncoder(nn.Module):
    def __init__(self, input_size):
        super().__init__()


        self.encoder_norm = LayerNorm(input_size)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=input_size, nhead=1
        )

        self.encoder = nn.TransformerEncoder(
            encoder_layer,
            1,
            norm=self.encoder_norm,
            enable_nested_tensor=True,
            mask_check=True,
        )

    def forward(self, x):
        batch_size = x.payload.size()[0]
        seq_len_max = x.payload.size()[1]
        

        out = self.encoder(x.payload)

        return PaddedBatch(out, x.seq_lens)
