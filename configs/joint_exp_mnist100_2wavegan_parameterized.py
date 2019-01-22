"""Config for MNIST <> WaveGAN transfer.
"""

# pylint:disable=invalid-name

from functools import partial

import tensorflow as tf

import model_joint

FLAGS = tf.flags.FLAGS

n_latent_A = 100
n_latent_B = 100
n_latent_shared = FLAGS.n_latent_shared
layers = (128,) * 4
layers_B = (2048,) * 8
batch_size = 128

Encoder = partial(
    model_joint.EncoderLatentFull,
    input_size=n_latent_A,
    output_size=n_latent_shared,
    layers=layers)

Decoder = partial(
    model_joint.DecoderLatentFull,
    input_size=n_latent_shared,
    output_size=n_latent_A,
    layers=layers)

vae_config_A = {
    'Encoder': Encoder,
    'Decoder': Decoder,
    'prior_loss_beta': FLAGS.prior_loss_beta_A,
    'prior_loss': 'KL',
    'batch_size': batch_size,
    'n_latent': n_latent_A,
    'n_latent_shared': n_latent_shared,
}


def make_Encoder_B(n_latent):
  return partial(
      model_joint.EncoderLatentFull,
      input_size=n_latent,
      output_size=n_latent_shared,
      layers=layers_B,
  )


def make_Decoder_B(n_latent):
  return partial(
      model_joint.DecoderLatentFull,
      input_size=n_latent_shared,
      output_size=n_latent,
      layers=layers_B,
  )


wavegan_config_B = {
    'Encoder': make_Encoder_B(n_latent_B),
    'Decoder': make_Decoder_B(n_latent_B),
    'prior_loss_beta': FLAGS.prior_loss_beta_B,
    'prior_loss': 'KL',
    'batch_size': batch_size,
    'n_latent': n_latent_B,
    'n_latent_shared': n_latent_shared,
}

config = {
    'vae_A': vae_config_A,
    'vae_B': wavegan_config_B,
    'config_A': 'mnist_0_nlatent100',
    'config_B': 'wavegan',
    'config_classifier_A': 'mnist_classifier_0',
    'config_classifier_B': '<unused>',
    # model
    'prior_loss_align_beta': FLAGS.prior_loss_align_beta,
    'mean_recons_A_align_beta': FLAGS.mean_recons_A_align_beta,
    'mean_recons_B_align_beta': FLAGS.mean_recons_B_align_beta,
    'mean_recons_A_to_B_align_beta': FLAGS.mean_recons_A_to_B_align_beta,
    'mean_recons_B_to_A_align_beta': FLAGS.mean_recons_B_to_A_align_beta,
    'pairing_number': FLAGS.pairing_number,
    # training dynamics
    'batch_size': batch_size,
    'n_latent_shared': n_latent_shared,
}
