"""Common functions/helpers for dataspace model.

This library contains many common functions and helpers used to for the
dataspace model (defined in `train_dataspace.py`) that is used in training
(`train_dataspace.py` and `train_dataspace_classifier.py`), sampling
(`sample_dataspace.py`) and encoding (`encode_dataspace.py`).
These components are classified in the following categories:

  - Loading helper that makes dealing with config / dataset easier. This
    includes:
        `get_model_uid`, `load_config`, `dataset_is_mnist_family`,
        `load_dataset`, `get_index_grouped_by_label`.

  - Helper making dumping dataspace data easier. This includes:
        `batch_image`, `save_image`, `make_grid`, `post_proc`

  - Miscellaneous Helpers, including
        `get_default_scratch`, `ObjectBlob`,

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from functools import partial
import importlib
import os

import librosa
from matplotlib import cm
import numpy as np
from PIL import Image
import tensorflow as tf

import local_mnist

FLAGS = tf.flags.FLAGS

tf.flags.DEFINE_string(
    'default_scratch', '/tmp/', 'The default root directory for scratching. '
    'It can contain \'~\' which would be handled correctly.')


def get_default_scratch():
  """Get the default directory for scratching."""
  return os.path.expanduser(FLAGS.default_scratch)


class ObjectBlob(object):
  """Helper object storing key-value pairs as attributes."""

  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      self.__dict__[k] = v


def get_model_uid(config_name, exp_uid):
  """Helper function returning model's uid."""
  return config_name + exp_uid


def load_config(config_name):
  """Load config from corresponding configs.<config_name> module."""
  return importlib.import_module('configs.%s' % config_name).config


def _load_celeba(data_path, postfix):
  """Load the CelebA dataset."""
  with tf.gfile.Open(os.path.join(data_path, 'train' + postfix), 'rb') as f:
    train_data = np.load(f)
  with tf.gfile.Open(os.path.join(data_path, 'eval' + postfix), 'rb') as f:
    eval_data = np.load(f)
  with tf.gfile.Open(os.path.join(data_path, 'test' + postfix), 'rb') as f:
    test_data = np.load(f)
  with tf.gfile.Open(os.path.join(data_path, 'attr_train.npy'), 'rb') as f:
    attr_train = np.load(f)
  with tf.gfile.Open(os.path.join(data_path, 'attr_eval.npy'), 'rb') as f:
    attr_eval = np.load(f)
  with tf.gfile.Open(os.path.join(data_path, 'attr_test.npy'), 'rb') as f:
    attr_test = np.load(f)
  attr_mask = [4, 8, 9, 11, 15, 20, 24, 31, 35, 39]
  attribute_names = [
      'Bald',
      'Black_Hair',
      'Blond_Hair',
      'Brown_Hair',
      'Eyeglasses',
      'Male',
      'No_Beard',
      'Smiling',
      'Wearing_Hat',
      'Young',
  ]
  attr_train = attr_train[:, attr_mask]
  attr_eval = attr_eval[:, attr_mask]
  attr_test = attr_test[:, attr_mask]
  return (train_data, eval_data, test_data, attr_train, attr_eval, attr_test,
          attribute_names)


def config_is_mnist_family(config):
  return dataset_is_mnist_family(config['dataset'])


def config_is_wavegan(config):
  return dataset_is_wavegan(config['dataset'])


def dataset_is_mnist_family(dataset):
  """returns if dataset is of MNIST family."""
  return dataset.lower() == 'mnist' or dataset.lower() == 'fashion-mnist'


def dataset_is_wavegan(dataset):
  """returns if dataset is WaveGAN."""
  return dataset.lower() == 'wavegan'


def load_dataset(config):
  """Load dataset following instruction in `config`."""
  if dataset_is_mnist_family(config['dataset']):
    crop_width = config.get('crop_width', None)  # unused
    img_width = config.get('img_width', None)  # unused

    scratch = config.get('scratch', get_default_scratch())
    basepath = os.path.join(scratch, config['dataset'].lower())
    data_path = os.path.join(basepath, 'data')
    save_path = os.path.join(basepath, 'ckpts')

    tf.gfile.MakeDirs(data_path)
    tf.gfile.MakeDirs(save_path)

    # black-on-white MNIST (harder to learn than white-on-black MNIST)
    # Running locally (pre-download data locally)
    mnist_train, mnist_eval, mnist_test = local_mnist.read_data_sets(
        data_path, one_hot=True)

    train_data = np.concatenate([mnist_train.images, mnist_eval.images], axis=0)
    attr_train = np.concatenate([mnist_train.labels, mnist_eval.labels], axis=0)
    eval_data = mnist_test.images
    attr_eval = mnist_test.labels

    attribute_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

  elif config['dataset'] == 'CELEBA':
    crop_width = config['crop_width']
    img_width = config['img_width']
    postfix = '_crop_%d_res_%d.npy' % (crop_width, img_width)

    # Load Data
    scratch = config.get('scratch', get_default_scratch())
    basepath = os.path.join(scratch, 'celeba')
    data_path = os.path.join(basepath, 'data')
    save_path = os.path.join(basepath, 'ckpts')

    (train_data, eval_data, _, attr_train, attr_eval, _,
     attribute_names) = _load_celeba(data_path, postfix)
  else:
    raise NotImplementedError

  return ObjectBlob(
      crop_width=crop_width,
      img_width=img_width,
      basepath=basepath,
      data_path=data_path,
      save_path=save_path,
      train_data=train_data,
      attr_train=attr_train,
      eval_data=eval_data,
      attr_eval=attr_eval,
      attribute_names=attribute_names,
  )


def get_index_grouped_by_label(label):
  """Get (an array of) index grouped by label.

  This array is used for label-level sampling.
  It aims at MNIST and CelebA (in Jesse et al. 2018) with 10 labels.

  Args:
    label: a list of labels in integer.

  Returns:
    A (# label - sized) list of lists contatining indices of that label.
  """
  index_grouped_by_label = [[] for _ in range(10)]
  for i, label in enumerate(label):
    index_grouped_by_label[label].append(i)
  return index_grouped_by_label


def audio_to_spectrum(audio_batch):

  def convert_(audio):
    spectrogram = librosa.feature.melspectrogram(
        audio[:16384], sr=16000, n_mels=64, n_fft=512, hop_length=256)
    log_amp = librosa.core.amplitude_to_db(spectrogram)[::-1, :]
    return log_amp

  audio_batch = audio_batch[:100]

  specturm_batch = [convert_(audio) for audio in audio_batch]
  specturm_batch = np.array(specturm_batch)
  specturm_batch = np.clip(specturm_batch, -100.0, 0.0) / 100.0 + 1.0
  for index_b in range(specturm_batch.shape[0]):
    min_v_ = specturm_batch[index_b].min()
    max_v_ = specturm_batch[index_b].max()
    specturm_batch[
        index_b] = (specturm_batch[index_b] - min_v_) / (max_v_ - min_v_)
  # [0., 1.0], means -100 to 0 e.g. 100db to 0db

  # http://thomas-cokelaer.info/blog/2014/09/about-matplotlib-colormap-and-how-to-get-rgb-values-of-the-map/

  img = np.zeros(list(specturm_batch.shape) + [3])
  for index_b in range(specturm_batch.shape[0]):
    for index_x in range(specturm_batch.shape[1]):
      for index_y in range(specturm_batch.shape[2]):
        v = int(specturm_batch[index_b][index_x][index_y] * 255)
        r, g, b, _ = cm.inferno(v)
        img[index_b][index_x][index_y] = [r, g, b]

  # specturm_batch = np.clip(specturm_batch, -100.0, 0.0) / 100.0 + 1.0
  # [0., 1.0], means -100 to 0 e.g. 100db to 0db
  # img = np.stack((specturm_batch,) * 3, -1)  # grey -> rgb
  return img


def batch_audio(b, max_samples=60):
  audio = b[:max_samples]
  audio = audio.reshape(-1)
  return audio


def batch_image(b, max_images=60, rows=6, cols=10):
  """Turn a batch of images into a single image mosaic."""
  mb = min(b.shape[0], max_images)
  if rows is None:
    rows = int(np.ceil(np.sqrt(mb)))
    cols = rows
  diff = rows * cols - mb
  b = np.vstack([b[:mb], np.zeros([diff, b.shape[1], b.shape[2], b.shape[3]])])
  tmp = b.reshape(-1, cols * b.shape[1], b.shape[2], b.shape[3])
  img = np.hstack(tmp[i] for i in range(rows))
  return img


def save_image(img, filepath):
  """Save an image to filepath.

  It assumes `img` is a float numpy array with value in [0, 1]

  Args:
    img: a float numpy array with value in [0, 1] representing the image.
    filepath: a string of file path.
  """
  img = np.maximum(0, np.minimum(1, img))
  im = Image.fromarray(np.uint8(img * 255))
  im.save(filepath)


def make_grid(boundary=2.0, number_grid=50, dim_latent=2):
  """Helper function making 1D or 2D grid for evaluation purpose."""
  zs = np.linspace(-boundary, boundary, number_grid)
  z_grid = []
  if dim_latent == 1:
    for x in range(number_grid):
      z_grid.append([zs[x]])
    dim_grid = 1
  else:
    for x in range(number_grid):
      for y in range(number_grid):
        z_grid.append([0.] * (dim_latent - 2) + [zs[x], zs[y]])
    dim_grid = 2
  z_grid = np.array(z_grid)
  return ObjectBlob(z_grid=z_grid, dim_grid=dim_grid)


def make_batch_image_grid(dim_grid, number_grid):
  """Returns a patched `make_grid` function for grid."""
  assert dim_grid in (1, 2)
  if dim_grid == 1:
    batch_image_grid = partial(
        batch_image,
        max_images=number_grid,
        rows=1,
        cols=number_grid,
    )
  else:
    batch_image_grid = partial(
        batch_image,
        max_images=number_grid * number_grid,
        rows=number_grid,
        cols=number_grid,
    )
  return batch_image_grid


def post_proc(img, config, emphasize=None, emphasize_color=(1.0, 0.0, 0.0)):
  """Post process image `img` according to the dataset in `config`."""
  x = img
  x = np.minimum(1., np.maximum(0., x))  # clipping
  if dataset_is_mnist_family(config['dataset']):
    x = np.reshape(x, (-1, 28, 28))
    x = np.stack((x,) * 3, -1)  # grey -> rgb
  if emphasize is not None:
    for i in emphasize:
      # Draw a border
      border_size = ((max(x.shape[1], x.shape[2]) + 31) // 32)
      for border_pos in range(border_size):
        x[i, 0 + border_pos, :] = list(emphasize_color)
        x[i, -1 - border_pos, :] = list(emphasize_color)
        x[i, :, 0 + border_pos] = list(emphasize_color)
        x[i, :, -1 - border_pos] = list(emphasize_color)
  return x
