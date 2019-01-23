# (Anonymous) Code for ICML 2019 Submission

This is the anonymous Github repository containing code for the submission to ICML 2019 titled
"_Latent Translation: Crossing Modalities by Bridging Generative Models Supplementary Materials_".

## Walkthrough of Experiments

A walkthrough of the experiments is available as follows:

1. Make pre-trained model for data space (VAE and classifier) using `train_dataspace.py` and `train_dataspace_classifier.py`.
2. Using pre-trained model, encode data to latent space using `encode_dataspace.py`, and optionally sample from latent space using `sample_dataspace.py` and `sample_wavegan.py`.
3. Training our method (our joint, bridging VAE using  `train_join.py` and `train_joint2_mnist_family.py`. A proof-of-concept of our method in a toy dataset is available as `poc_joint2_exp1.py`.
4. Visualizing and evaluating our model using  `interpolate_joint.py` and `evaluate_joint2_mnist_family.py`.

For details, a history of all commands used to invoke running of code is kept under `notes_and_commands/`.

## List of Files

An overview of code files and their functionality is here provided here:

- `train_join.py` and `train_joint2_mnist_family.py`: Training our joint bridging VAE.
- `poc_joint2_exp1.py`: Proof-of-concept for joint bridging VAE in a toy dataset in our paper.
- `train_dataspace.py` and `train_dataspace_classifier.py`: Training of vae models and classifiers in dataspace, serving as preparing pre-trained models in paper.
- `encode_dataspace.py`: Encoding data into latent space using pre-trained models.
- `sample_dataspace.py` and `sample_wavegan.py`: Sampling from latent space using pre-trained models.
- `interpolate_joint.py`: Evaluating thorough interpolating of our model in the paper.
- `evaluate_joint2_mnist_family.py`: Evaluating our model in the paper.
- `nn.py` and `model*.py`: Neural network models.
- `common*.py`: Common utilities.
- `local_mnist.py`: MNIST helpers.
- `configs/*.py`: The configurations for different runs in experiments.
- `notes_and_commands/*`: Notes containing invoked commands used to call training/evaluating.


