# Primer

The background this project needs, one topic per section. Read the section an issue points
to when you start that issue; you do not need the rest yet. Terms in **bold** are in the
glossary (section 10).

## 1. Images, voxels and affines

A structural MRI scan is a 3D array of numbers. Each element is a **voxel** (volume element),
the 3D version of a pixel: its value is the signal measured in a small box of tissue. The
array alone does not say where things are. An image file also stores the voxel size, in
millimetres (a voxel can be 0.5 x 0.5 x 1.5 mm, not a cube), and an **affine**: a 4x4 matrix
`A` that maps voxel indices to positions in millimetres,

```
[x, y, z, 1] = A @ [i, j, k, 1]
```

The upper-left 3x3 block holds the voxel sizes and the rotation; the last column is the
position of voxel `(0, 0, 0)`. Images are stored as NIfTI files (`.nii.gz`) and read with
nibabel:

```python
import nibabel as nb

img = nb.load("data/human/brain.nii.gz")
data = img.get_fdata()           # numpy array
img.affine                       # the 4x4 matrix
img.header.get_zooms()           # voxel sizes in mm
nb.aff2axcodes(img.affine)       # orientation, e.g. ('L', 'I', 'A')
```

The **orientation** codes say where each array axis points: `('L', 'I', 'A')` means that `i`
grows towards the subject's left, `j` towards inferior (the feet), and `k` towards anterior
(the nose). Two files can hold the same head in different orientations, so always compare
images in millimetres, through their affines, and never by array index alone.

Macaques are often scanned lying in a "sphinx" position, so the orientation in the header can
be wrong. The dataset you receive has this fixed.

## 2. Skull stripping and brain masks

A head MRI shows the brain and everything around it: skull, scalp, eyes, muscle, fat.
**Skull stripping** (brain extraction) decides which voxels belong to the brain. The result
is a **brain mask**: an array of the same shape as the image, 1 inside the brain and 0
outside. Almost every brain-imaging analysis starts with it, because later steps
(registration, tissue segmentation) go wrong when they see the skull.

Skull stripping is a **segmentation** with two classes, background and brain. A network for
it outputs, for every voxel, one score per class; the predicted class is the one with the
highest score, the **argmax**.

## 3. MeshNet and MindGrab

MindGrab is a **MeshNet**: a stack of 3D convolutions with no pooling and no upsampling, so
every layer keeps the full 256x256x256 size of its input. To see far without shrinking the
image, MeshNet uses **dilated convolutions**: a 3x3x3 kernel whose taps are `d` voxels apart.
With dilation 16, one kernel spans 33 voxels.

MindGrab has 26 layers: five blocks of five convolutions with dilations 16, 8, 4, 2 and 1,
then a 1x1x1 convolution that gives the two class scores. Each of the 25 hidden layers is:

1. a 3D convolution with 15 output channels and no bias;
2. a **group normalisation** with one group per channel and no learnable scale: each channel
   is shifted and scaled to mean 0 and variance 1, over the whole input volume;
3. a GELU activation.

Each dilated layer lets a voxel look `d` voxels further in every direction, so the
**receptive field** grows to 311 voxels: wider than the whole 256-voxel grid. The network
has 146,237 parameters: 405 in the first layer (1 x 15 x 27), 6,075 in each of the 24 other
hidden layers (15 x 15 x 27), and 32 in the last one (15 x 2 weights and 2 biases).

PyTorch stores the weights as a **state dict**: a dictionary from layer names to tensors.
`model.3.0.weight` is the weight of the first module (the convolution) of layer 3. Loading a
state dict with `strict=True` fails if a single name or shape differs, which makes it the
best test that your network is MindGrab's.

Before running the network, BrainChop conforms the image (section 4), then maps the 2nd
intensity percentile to 0 and the 98th to 1, and clips to the range 0 to 1.

## 4. Conforming and voxel scaling

**Conforming** resamples an image onto a fixed grid: 256x256x256 voxels of 1 mm, in one fixed
orientation (BrainChop uses LIA). For every voxel of the new grid, resampling computes its
position in millimetres and reads the old image there. Between old voxels it interpolates:
linearly (`order=1`) for images, and with the nearest neighbour (`order=0`) for masks, which
must stay 0 or 1.

A human brain is about 1,200 cc, a macaque brain about 90 cc: 13 times smaller in volume,
about 2.4 times along each axis. Conformed at 1 mm, a macaque brain fills a small part of the
grid and looks nothing like what MindGrab learned. **Voxel scaling** pretends that each voxel
is `s` times larger, by multiplying the 3x3 block of the affine by `s`. After conforming, the
brain is `s` times larger along each axis and `s**3` times in volume. Scaling the affine by
`s` and conforming at 1 mm gives the same array as conforming at `1/s` mm; the BrainChop
lab's rodent model does the latter, at 0.1 mm.

Scaling changes the millimetres. A volume measured on the conformed grid must be divided by
`s**3` to be real, and a distance by `s`.

A round trip (conform, then back to the native grid) is never exact with nearest-neighbour
interpolation: the two grids do not line up, so voxels on the edge of a mask can flip. A
round-trip Dice (section 5) a little below 1 is expected; a much lower one means a bug, such
as a swapped axis.

## 5. Measuring agreement

Three numbers compare a predicted mask `P` with a reference mask `R`:

- **Dice** `= 2 |P and R| / (|P| + |R|)`, from 0 (no overlap) to 1 (identical). Dice barely
  moves when a thin layer of skull is included, because the brain is large.
- **HD95**: for every surface voxel of each mask, the distance to the nearest surface voxel of
  the other; HD95 is the 95th percentile of these distances, in millimetres. It catches leaks
  into skull, eyes or muscle that Dice hides.
- **Volume error**: the predicted minus the reference brain volume, in cubic centimetres and in
  percent. It shows a systematic over- or under-segmentation.

Distances and volumes must use the voxel sizes, since voxels are often not cubes.

## 6. The data: PRIME-DE and imperfect labels

PRIME-DE, the PRIMate Data Exchange, shares MRI of about 900 macaques from 32 **sites**
(laboratories), on scanners of 1.5 to 7 tesla. Each site has its own scanner, head coil,
sequence and way of handling the animals, so images of two sites can differ a lot in
contrast, noise, field of view and **bias field** (a slow change of brightness across the
image).

In supervised training the **label** is the answer the model should give: here, the brain
mask. Most labels in this project were made by other tools and checked by eye; only a few
were edited by hand. A tool-made mask can include a bit of skull or miss a bit of brain. A
model trained on such labels learns their mistakes too, and a model tested against them is
rewarded for copying them. That is why the test references are, where possible, masks edited
by hand.

## 7. Splitting by site

The data are split three ways. The **training** set updates the weights. The **validation**
set decides everything else: when to stop training, which learning rate, which scale factor
`s`. The **test** set is used once, at the end, to report the result.

Here the split is by site. A model tested on new scans from a site it trained on knows that
site's scanner, so its score overestimates what happens at a new laboratory. Holding out
whole sites measures what we care about: how the model does on a scanner it has never seen.

**Cross-validation** repeats the split so that every subject is tested once; in
**leave-one-site-out** cross-validation each site in turn is the test site, and the model is
retrained each time. This project starts with a single split (two training sites, one
validation site, one test site); the full cross-validation is a stretch goal.

Never choose anything by looking at the test site. A choice made on test data makes the
reported score optimistic, and the error cannot be undone afterwards.

## 8. How MindGrab was trained, and what fine-tuning changes

MindGrab never saw a real MRI scan during training. It learned from synthetic images
generated from **label maps**: volumes in which every voxel carries an anatomical label (grey
matter, white matter, fluid, skull, eyes, and so on). For every training sample, a generator
picks a random intensity for each label, deforms the map, and adds blur, noise and bias field,
so every sample looks like a scan from a different scanner. The training target is the union
of the brain labels. This is **domain randomisation**: by seeing every possible contrast, the
network learns to recognise the brain's shape rather than one scanner's look. The MindGrab
paper (section 2.2) gives the details: 171 label maps with 39 labels, the Adam optimiser, a
soft Dice loss, a one-cycle learning-rate schedule, batches of one volume.

**Fine-tuning** starts from MindGrab's weights and continues training on macaque data with a
small learning rate, so the model keeps what it knows about heads and adapts to monkeys. In
this project the training pairs are real macaque images with their masks. The training loop
does not care where an image comes from: a data loader hands it `(image, label)` pairs. The
same code could later learn from synthetic macaque images instead.

## 9. Compute: devices, crops and memory

PyTorch runs on three kinds of **device**: `cuda` (an NVIDIA GPU), `mps` (the GPU of Apple
laptops) and `cpu`. The `mps` device does not support `float64`, so keep arrays and tensors in
`float32`.

Training needs memory. Every hidden layer produces 15 channels at full size; at 256^3 that is
about 1 GB per layer in `float32`, and the backward pass keeps the outputs of all 25 layers.
Two remedies, often combined:

- **Crops**: train on random sub-volumes, for example 128^3 (8 times fewer voxels). On an
  Apple M4 laptop, one training step takes 3.6 s on a 96^3 crop, 8.9 s on 128^3, and 190 s on
  160^3 because the machine runs out of memory. The catch: group normalisation computes its
  statistics over the whole input, so statistics on a crop differ from those on the full
  volume used at inference. The BrainChop lab trains on crops that grow during training, up to
  the full volume.
- **Gradient checkpointing** (`torch.utils.checkpoint`) keeps only some layer outputs and
  recomputes the others during the backward pass: less memory, more time.

## 10. Glossary

| Term | Meaning |
|---|---|
| affine | 4x4 matrix mapping voxel indices to millimetres (section 1) |
| argmax | the index of the largest value; the predicted class per voxel |
| bias field | slow change of image brightness across the field of view |
| brain mask | array of 0s and 1s marking the brain's voxels |
| conform | resample to 256^3 voxels of 1 mm in a fixed orientation (section 4) |
| crop | a sub-volume of the image used for training |
| cross-validation | repeating train/test splits so every subject is tested once |
| device | where PyTorch computes: `cuda`, `mps` or `cpu` |
| Dice | overlap of two masks, from 0 to 1 (section 5) |
| dilated convolution | convolution whose kernel taps are spaced `d` voxels apart |
| domain randomisation | training on synthetic images with random contrasts (section 8) |
| fine-tuning | continuing the training of a trained model on new data |
| group normalisation | per-channel rescaling to mean 0 and variance 1 |
| HD95 | 95th percentile of surface distances, in mm (section 5) |
| label, label map | the answer for training: a mask, or a map of anatomical labels |
| leave-one-site-out | cross-validation in which each site is the test site once |
| MeshNet | convolution-only network that keeps the full image size |
| NIfTI | the file format of the images (`.nii`, `.nii.gz`) |
| orientation | where each array axis points, e.g. LIA (section 1) |
| receptive field | the region of the input a voxel's prediction can see |
| segmentation | assigning a class to every voxel |
| site | one laboratory, with its scanner and protocol |
| skull stripping | computing the brain mask of a head image |
| state dict | PyTorch's dictionary of layer names to weight tensors |
| validation set | data that guide choices during training; never the test set |
| voxel | one element of the 3D image array |
| voxel scaling | multiplying the affine by `s` so a small brain looks human-sized |
