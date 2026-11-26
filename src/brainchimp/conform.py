"""
Ref
    - https://nipy.org/nibabel/coordinate_systems.html
    - https://nipy.org/nibabel/reference/nibabel.processing.html
"""

import nibabel as nib
import nibabel.processing


def _scale_img(img, scale):
    A = img.affine.copy()
    A[:3, :3] *= scale
    return nib.Nifti1Image(img.dataobj, A, img.header)


def conform(img, scale, order):
    """
    order = 1 for img, linear interpolation
    order = 0 for mask, nearest neighbor
    """

    scaled_img = _scale_img(img, scale)
    return nib.processing.conform(
        scaled_img,
        out_shape=(256, 256, 256),
        voxel_size=(1.0, 1.0, 1.0),
        order=order,
        orientation="LIA",
    )


def unconform(mask, reference, scale):
    scaled_ref = _scale_img(reference, scale)
    resampled = nib.processing.resample_from_to(mask, scaled_ref, order=0)
    return nib.Nifti1Image(resampled.get_fdata(), reference.affine, reference.header)


if __name__ == "__main__":
    pass
