# Sports Dataset for AI Activity Recognition

This directory houses the balanced 7-class video dataset assembled from UCF101 and HMDB51, along with isolated kinematic touchdown clips and verified sports execution videos.

## Class Breakdown & Statistics (Total: 1,537 Clips)

| Class Name | Directory | Video Clips Count | Primary Source Categories |
| :--- | :--- | :--- | :--- |
| **Jumping** | `jumping/` | 341 | UCF101 HighJump, LongJump |
| **Squatting** | `squatting/` | 114 | UCF101 BodyWeightSquats |
| **Sprinting** | `sprinting/` | 133 | HMDB51 Running, Athletics Sprints |
| **Landing** | `landing/` | 123 | Ground-contact & impact flexion phases isolated from jump trials |
| **Throwing** | `throwing/` | 341 | UCF101 JavelinThrow, Shotput, ThrowDiscus |
| **Cutting Movements** | `cutting_movements/` | 140 | HMDB51 Pivots, Sharp Directional Changes & Turns |
| **Sports Specific Drills** | `sports_specific_drills/` | 345 | UCF101 SoccerJuggling, BaseballPitch, Athletics Drills |

## Feature Extraction

All clips are processed through `ml/extract_features.py` using YOLOv8 pose estimation, extracting a 95-dimensional kinematic vector across 32 normalized temporal frames. The pre-extracted dataset is preserved in `ml/dataset_features.npz`.
