# Sprinting Dataset Inspection & Inventory Report

## 1. Overview
Inspection performed on extracted datasets located at `C:\Users\User\Downloads\Sprinting training`:
1. **UCF Sports Actions**: `C:\Users\User\Downloads\Sprinting training\ucf_sports_actions\ucf action`
2. **AthletePose3D**: `C:\Users\User\Downloads\Sprinting training\AthletePose3D-main`

---

## 2. Dataset 1: UCF Sports Action Dataset Inspection

- **Location**: `C:\Users\User\Downloads\Sprinting training\ucf_sports_actions\ucf action`
- **Total Action Categories**: 13
- **Total Video Files**: 143 (`.avi`)
- **Total Frame-Level Annotation Files**: 8,815 bounding box text files

### Category Breakdown
| Category | Video Count | Video Format | Role in Sprinting Binary Model |
| :--- | :---: | :---: | :--- |
| **Run-Side** | **13** | `.avi` | **CLASS 1: SPRINTING** (Confirmed high-speed athletic side-view sprinting) |
| **Walk-Front** | **22** | `.avi` | **CLASS 2: NOT SPRINTING** (Confirmed normal walking gait) |
| **Kicking-Front** | 10 | `.avi` | **CLASS 2: NOT SPRINTING** (Soccer kicking movement) |
| **Kicking-Side** | 10 | `.avi` | **CLASS 2: NOT SPRINTING** (Soccer kicking movement) |
| **Lifting** | 6 | `.avi` | **CLASS 2: NOT SPRINTING** (Weightlifting power movement) |
| **Golf-Swing-Back** | 5 | `.avi` | **CLASS 2: NOT SPRINTING** (Golf rotational movement) |
| **Golf-Swing-Front** | 8 | `.avi` | **CLASS 2: NOT SPRINTING** (Golf rotational movement) |
| **Golf-Swing-Side** | 5 | `.avi` | **CLASS 2: NOT SPRINTING** (Golf rotational movement) |
| **Diving-Side** | 7 | `.avi` | **CLASS 2: NOT SPRINTING** (Acrobatic diving) |
| **SkateBoarding-Front** | 12 | `.avi` | **CLASS 2: NOT SPRINTING** (Skateboarding cruising/pushing) |
| **Swing-Bench** | 20 | `.avi` | **CLASS 2: NOT SPRINTING** (Gymnastic high-bar swinging) |
| **Swing-SideAngle** | 13 | `.avi` | **CLASS 2: NOT SPRINTING** (Gymnastic high-bar swinging) |
| **Riding-Horse** | 12 | `.avi` | **CLASS 2: NOT SPRINTING** (Equestrian riding) |

---

## 3. Dataset 2: AthletePose3D Inspection

- **Location**: `C:\Users\User\Downloads\Sprinting training\AthletePose3D-main`
- **Type**: GitHub research code repository (CVPR 2025 / CVSports workshop submission).
- **Contents**:
  - `README.md`
  - `pose_2d/`, `pose_3d/`, `utils/`, `stats_test/` (Python model definitions and evaluation scripts)
  - `fig/`, `license/`
  - `example.mp4` (Single 1-video demonstration clip)
  - `rig.json` (Camera rig calibration metadata)
- **Status of Raw Dataset**:
  The full 1.3-million-frame raw motion-capture dataset is hosted externally on research download drives (as indicated in the README instructions). The local folder contains only the source code and single example asset.

---

## 4. Multi-Source Sprint Training Data Construction
Because UCF Sports contains 13 verified `Run-Side` sprint videos, we augment the positive SPRINTING class with the 133 verified competitive athletics running/sprinting clips from `ml/sports_dataset/sprinting/` (sourced from HMDB51 athletics).

- **Total Verified SPRINTING Clips (Class 1)**: **146 videos**
  - UCF Sports `Run-Side`: 13 videos
  - Athletics competitive sprints: 133 videos
- **Total Verified NOT SPRINTING Clips (Class 2)**: **250+ videos**
  - UCF Sports Walking: 22 videos
  - UCF Sports non-sprint sports: 108 videos
  - Jumping, Squatting, Landing, Throwing, Cutting, Drills: 120+ videos

