"""Config for transfer between MNIST families.
"""

# pylint:disable=invalid-name

from functools import partial

import tensorflow as tf

import model_joint

FLAGS = tf.flags.FLAGS

n_latent = FLAGS.n_latent
n_latent_shared = FLAGS.n_latent_shared
layers = (512,) * 8
batch_size = 128

Encoder = partial(
    model_joint.EncoderLatentFull,
    input_size=n_latent,
    output_size=n_latent_shared,
    layers=layers)

Decoder = partial(
    model_joint.DecoderLatentFull,
    input_size=n_latent_shared,
    output_size=n_latent,
    layers=layers)

vae_config_A = {
    'Encoder': Encoder,
    'Decoder': Decoder,
    'prior_loss_beta': FLAGS.prior_loss_beta_A,
    'prior_loss': 'KL',
    'batch_size': batch_size,
    'n_latent': n_latent,
    'n_latent_shared': n_latent_shared,
}

vae_config_B = {
    'Encoder': Encoder,
    'Decoder': Decoder,
    'prior_loss_beta': FLAGS.prior_loss_beta_B,
    'prior_loss': 'KL',
    'batch_size': batch_size,
    'n_latent': n_latent,
    'n_latent_shared': n_latent_shared,
}

config = {
    'vae_A': vae_config_A,
    'vae_B': vae_config_B,
    'config_A': FLAGS.mnist_family_config_A,
    'config_B': FLAGS.mnist_family_config_B,
    'config_classifier_A': FLAGS.mnist_family_config_classifier_A,
    'config_classifier_B': FLAGS.mnist_family_config_classifier_B,
    # model
    'prior_loss_align_beta': FLAGS.prior_loss_align_beta,
    'mean_recons_A_align_beta': FLAGS.mean_recons_A_align_beta,
    'mean_recons_B_align_beta': FLAGS.mean_recons_B_align_beta,
    'mean_recons_A_to_B_align_beta': FLAGS.mean_recons_A_to_B_align_beta,
    'mean_recons_B_to_A_align_beta': FLAGS.mean_recons_B_to_A_align_beta,
    'mean_recons_A_to_B_align_free_budget': FLAGS.mean_recons_A_to_B_align_free_budget,
    'mean_recons_B_to_A_align_free_budget': FLAGS.mean_recons_B_to_A_align_free_budget,
    'pairing_number': FLAGS.pairing_number,
    # training dynamics
    'batch_size': batch_size,
    'n_latent': n_latent,
    'n_latent_shared': n_latent_shared,
    'lr': FLAGS.lr,
}
