# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-Apache2
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest

from bionemo.core.data.load import load
from bionemo.esm2.data import tokenizer
from bionemo.esm2.model.finetune.finetune_regressor import (
    ESM2FineTuneSeqConfig,
    ESM2FineTuneSeqModel,
    MegatronMLPHead,
)
from bionemo.testing import megatron_parallel_state_utils


# To download a 8M internally pre-trained ESM2 model
pretrain_ckpt_path = load("esm2/nv_8m:2.0")


@pytest.fixture
def config():
    return ESM2FineTuneSeqConfig(encoder_frozen=True, ft_dropout=0.50, initial_ckpt_path=str(pretrain_ckpt_path))


@pytest.fixture
def finetune_seq_model(config):
    with megatron_parallel_state_utils.distributed_model_parallel_state():
        model = config.configure_model(tokenizer.get_tokenizer())
        yield model


def test_ft_config(config):
    assert config.initial_ckpt_skip_keys_with_these_prefixes == ["regression_head"]
    assert config.encoder_frozen
    assert config.ft_dropout == 0.50


def test_ft_model_initialized(finetune_seq_model):
    assert isinstance(finetune_seq_model, ESM2FineTuneSeqModel)
    assert isinstance(finetune_seq_model.regression_head, MegatronMLPHead)
    assert finetune_seq_model.post_process
    assert not finetune_seq_model.include_embeddings_finetuning
