# Media Viewer Specification

## Purpose

Provide inline preview of image and video files within the file detail panel.
The viewer is embedded — not a separate window — and activates on file click
in the file tree.

## Requirements

### Requirement: Image Preview

The system MUST render image files inline in the detail panel.
The system MUST support JPEG, PNG, HEIC, WebP, and GIF formats at minimum.

#### Scenario: User clicks an image in the file tree

- GIVEN the file tree is populated with copied files
- WHEN the user clicks on an image file
- THEN the image renders in the detail panel at fit-to-panel size

#### Scenario: Unsupported format

- GIVEN the user clicks a file with an unsupported extension (e.g., `.raw`, `.cr2`)
- WHEN the detail panel opens
- THEN a placeholder "Preview not available for this format" is shown
- AND metadata is still displayed normally

### Requirement: Video Preview

The system MUST support inline playback of MP4, MOV, and AVI files.
The system MUST provide play/pause controls and a seek bar.
The system MAY support volume control.

#### Scenario: User clicks a video file

- GIVEN the file tree contains a copied video
- WHEN the user clicks on it
- THEN the video renders in paused state with play/pause and seek controls visible

#### Scenario: Codec not supported by OS WebView

- GIVEN a video with a codec the WebView cannot decode
- WHEN the detail panel attempts playback
- THEN an error with the codec name is shown
- AND an "Open with system player" button is provided

### Requirement: Preview Navigation

The system SHOULD allow navigating to the next/previous file in the same
organized directory using keyboard arrow keys from within the detail panel.

#### Scenario: Arrow key navigation

- GIVEN an image is open in the detail panel
- WHEN the user presses the right arrow key
- THEN the next media file in the same destination directory is loaded
