import warnings
from typing import Any, Callable, Dict, Iterator, Mapping, Optional, Sequence, Tuple
from absl import app, flags
import os
import sys

import numpy
import tensorflow as tf
import jax
import jax.numpy as jnp
from jax import random, vmap, jit, grad, value_and_grad, hessian, jacfwd, jacrev

import flax
from flax.core import freeze, unfreeze
from flax import linen as nn
from flax import optim

from jax.config import config
config.enable_omnistaging() # Linen requires enabling omnistaging

key = random.PRNGKey(0)

warnings.filterwarnings("ignore", category=DeprecationWarning)
FLAGS = flags.FLAGS

# Define a command-line argument using the Abseil library:
# https://abseil.io/docs/python/guides/flags
flags.DEFINE_string('prefix', '***', 'Prefix on printed output for easy searching in logs')
flags.DEFINE_integer('ndims', 100, 'Number of dimensions.')

def pprint(str):
    print(f'{FLAGS.prefix} {str}')


def tf_test():
    pprint("tf version ", tf.__version__)  
    pprint("TF backend")
    try:
        pprint([d for d in tf.config.list_physical_devices()])
    except Exception as ex:
        # in <tf2.1, it was called tf.experimental.config.list_physical_devices
        pprint(ex)
    
        
def jax_test(ndims):
    pprint("jax version {}".format(jax.__version__))
    pprint("jax backend {}".format(jax.lib.xla_bridge.get_backend().platform))
    pprint(jax.devices())
        
    key = jax.random.PRNGKey(0)
    pprint(f"ndims = {ndims}")
    A = jax.random.normal(key, shape=(ndims, ndims))
    s, d = jnp.linalg.slogdet(A)
    print(s, d)

class MLP(nn.Module):
    features: Sequence[int]
    
    def setup(self):
      print('setup')
      self.layers = [nn.Dense(feat) for feat in self.features]
    
    def __call__(self, inputs):
      print('call')
      x = inputs
      for i, lyr in enumerate(self.layers):
        x = lyr(x)
        if i != len(self.layers) - 1:
          x = nn.relu(x)
      return x


def flax_test(ndims):
    pprint("flax version {}".format(flax.__version__))
    model = MLP([ndims, ndims])
    pprint(model)

def main(_):
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true' 
    jax_test(FLAGS.ndims)
    tf_test()
    flax_test(FLAGS.ndims)

        
if __name__ == '__main__':
    app.run(main)
