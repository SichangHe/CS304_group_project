#!/usr/bin/env python

# Copyright 2015-2016  Brno University of Technology (author: Karel Vesely)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

# Generated Nnet prototype, to be initialized by 'nnet-initialize'.

from __future__ import print_function

import sys

###
### Parse options
###
from optparse import OptionParser

usage = "%prog [options] <feat-dim> <num-leaves> >nnet-proto-file"
parser = OptionParser(usage)
# Required,
parser.add_option(
    "--cell-dim",
    dest="cell_dim",
    type="int",
    default=320,
    help="Number of cells for one direction in BLSTM [default: %default]",
)
parser.add_option(
    "--proj-dim",
    dest="proj_dim",
    type="int",
    default=200,
    help="Dim reduction for one direction in BLSTM [default: %default]",
)
parser.add_option(
    "--proj-dim-last",
    dest="proj_dim_last",
    type="int",
    default=320,
    help="Dim reduction for one direction in BLSTM (last BLSTM component) [default: %default]",
)
parser.add_option(
    "--num-layers",
    dest="num_layers",
    type="int",
    default=2,
    help="Number of BLSTM layers [default: %default]",
)
# Optional (default == 'None'),
parser.add_option(
    "--lstm-param-range",
    dest="lstm_param_range",
    type="float",
    help="Range of initial BLSTM parameters [default: %default]",
)
parser.add_option(
    "--param-stddev",
    dest="param_stddev",
    type="float",
    help="Standard deviation for initial weights of Softmax layer [default: %default]",
)
parser.add_option(
    "--cell-clip",
    dest="cell_clip",
    type="float",
    help="Clipping cell values during propagation (per-frame) [default: %default]",
)
parser.add_option(
    "--diff-clip",
    dest="diff_clip",
    type="float",
    help="Clipping partial-derivatives during BPTT (per-frame) [default: %default]",
)
parser.add_option(
    "--cell-diff-clip",
    dest="cell_diff_clip",
    type="float",
    help='Clipping partial-derivatives of "cells" during BPTT (per-frame, those accumulated by CEC) [default: %default]',
)
parser.add_option(
    "--grad-clip",
    dest="grad_clip",
    type="float",
    help="Clipping the accumulated gradients (per-updates) [default: %default]",
)
#

(o, args) = parser.parse_args()
if len(args) != 2:
    parser.print_help()
    sys.exit(1)

(feat_dim, num_leaves) = [int(i) for i in args]

# Original prototype from Jiayu,
# <NnetProto>
# <Transmit> <InputDim> 40 <OutputDim> 40
# <LstmProjectedStreams> <InputDim> 40 <OutputDim> 512 <CellDim> 800 <ParamScale> 0.01 <NumStream> 4
# <AffineTransform> <InputDim> 512 <OutputDim> 8000 <BiasMean> 0.000000 <BiasRange> 0.000000 <ParamStddev> 0.04
# <Softmax> <InputDim> 8000 <OutputDim> 8000
# </NnetProto>

lstm_extra_opts = ""
if None != o.lstm_param_range:
    lstm_extra_opts += "<ParamRange> %f " % o.lstm_param_range
if None != o.cell_clip:
    lstm_extra_opts += "<CellClip> %f " % o.cell_clip
if None != o.diff_clip:
    lstm_extra_opts += "<DiffClip> %f " % o.diff_clip
if None != o.cell_diff_clip:
    lstm_extra_opts += "<CellDiffClip> %f " % o.cell_diff_clip
if None != o.grad_clip:
    lstm_extra_opts += "<GradClip> %f " % o.grad_clip

softmax_affine_opts = ""
if None != o.param_stddev:
    softmax_affine_opts += "<ParamStddev> %f " % o.param_stddev

# The BLSTM layers,
if o.num_layers == 1:
    # Single BLSTM,
    print(
        "<BlstmProjected> <InputDim> %d <OutputDim> %d <CellDim> %s"
        % (feat_dim, 2 * o.proj_dim_last, o.cell_dim)
        + lstm_extra_opts
    )
else:
    # >1 BLSTM,
    print(
        "<BlstmProjected> <InputDim> %d <OutputDim> %d <CellDim> %s"
        % (feat_dim, 2 * o.proj_dim, o.cell_dim)
        + lstm_extra_opts
    )
    for l in range(o.num_layers - 2):
        print(
            "<BlstmProjected> <InputDim> %d <OutputDim> %d <CellDim> %s"
            % (2 * o.proj_dim, 2 * o.proj_dim, o.cell_dim)
            + lstm_extra_opts
        )
    print(
        "<BlstmProjected> <InputDim> %d <OutputDim> %d <CellDim> %s"
        % (2 * o.proj_dim, 2 * o.proj_dim_last, o.cell_dim)
        + lstm_extra_opts
    )

# Adding <Tanh> for more stability,
print(
    "<Tanh> <InputDim> %d <OutputDim> %d" % (2 * o.proj_dim_last, 2 * o.proj_dim_last)
)

# Softmax layer,
print(
    "<AffineTransform> <InputDim> %d <OutputDim> %d <BiasMean> 0.0 <BiasRange> 0.0"
    % (2 * o.proj_dim_last, num_leaves)
    + softmax_affine_opts
)
print("<Softmax> <InputDim> %d <OutputDim> %d" % (num_leaves, num_leaves))
