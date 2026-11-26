"""
Ref
    - https://karam-nus.github.io/metrics/docs/metrics/segmentation/dice
    - https://en.wikipedia.org/wiki/Hausdorff_distance
    - https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.distance_transform_edt.html
    - https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.binary_erosion.html
"""

import numpy as np
from scipy import ndimage


def dice(mask_truth, mask_pred):
    if mask_truth.shape != mask_pred.shape:
        raise ValueError("Mask have not the same shape")

    if mask_truth.sum() == 0 and mask_pred.sum() == 0:
        return 1

    TP = 0
    FP = 0
    FN = 0

    for i in range(mask_truth.shape[0]):
        for j in range(mask_truth.shape[1]):
            for k in range(mask_truth.shape[2]):
                T = mask_truth[i][j][k]
                P = mask_pred[i][j][k]
                if T == P:
                    if T:
                        TP += 1
                else:
                    if P:
                        FP += 1
                    else:
                        FN += 1

    return 2 * TP / (2 * TP + FP + FN)


def hd95(mask_truth, mask_pred, voxel_size):
    if mask_truth.shape != mask_pred.shape:
        raise ValueError("Mask have not the same shape")

    if len(voxel_size) != mask_truth.ndim:
        raise ValueError("Voxel size dimension do not correspond to mask dimension")

    surface_t = mask_truth & ~ndimage.binary_erosion(mask_truth)
    surface_p = mask_pred & ~ndimage.binary_erosion(mask_pred)

    if not surface_t.any() and not surface_p.any():
        return 0.0

    if not surface_t.any() or not surface_p.any():
        return float("inf")

    distance_to_t = ndimage.distance_transform_edt(~surface_t, sampling=voxel_size)
    distance_to_p = ndimage.distance_transform_edt(~surface_p, sampling=voxel_size)

    distances = np.concatenate((distance_to_p[surface_t], distance_to_t[surface_p]))

    return float(np.percentile(distances, 95))


def volume_error(mask_truth, mask_pred, voxel_size):
    if mask_truth.shape != mask_pred.shape:
        raise ValueError("Mask have not the same shape")

    if len(voxel_size) != mask_truth.ndim:
        raise ValueError("Voxel size dimension do not correspond to mask dimension")

    vol_t = mask_truth.sum() * np.prod(voxel_size)
    vol_p = mask_pred.sum() * np.prod(voxel_size)

    if vol_t == 0 and vol_p == 0:
        return (0.0, 0.0)

    if vol_t == 0:
        raise ZeroDivisionError

    error_mm3 = abs(vol_t - vol_p)
    error_cm3 = error_mm3 / 1000
    error_percent = error_mm3 * 100 / vol_t

    return float(error_percent), float(error_cm3)


if __name__ == "__main__":
    pass
