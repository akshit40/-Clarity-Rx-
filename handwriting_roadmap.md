# ML Engineering Roadmap: Advanced Handwriting Extraction 🩺

## Objective
To enable **Clarity Rx** to accurately process highly blurry, low-contrast, and complex medical handwriting ("doctor's scribble") by implementing a multi-stage Machine Learning pipeline.

---

## 🏗️ Phase 1: Image Intelligence (Preprocessing)
*Goal: Turn a "bad photo" into a "machine-readable" asset.*

1.  **Adaptive Thresholding**: Instead of global brightness, use local mean/Gaussian thresholds to handle uneven lighting in prescription photos.
2.  **Bilateral Denoising**: Removes sensor noise while preserving the sharp edges of the handwriting.
3.  **Perspective Correction**: Automatically detect the 4 corners of the paper and "flatten" it (Orthorectification) to avoid warped text.
4.  **Super-Resolution (ESRGAN)**: Use a Generative Adversarial Network to upscale blurry text, artificially reconstructing lost pixel detail.

## 🧠 Phase 2: Segmentation & Feature Detection
*Goal: Isolate the medicine names from the noise.*

1.  **Line Segmentation**: Detect individual lines of text. This prevents the AI from "bleeding" instructions from one medicine into another.
2.  **Word-Level Bounding Boxes**: Identify exactly where each word is located on the page.
3.  **Medical Entity Recognition (MER)**: Trained on medical datasets (PubMed, drug databases) to distinguish between a "Date", a "Medicine Name", and a "Dosage".

## 🚀 Phase 3: Extraction Strategy (LLM + Vision)
*Goal: Use the highest-tier reasoning available.*

1.  **Chain-of-Thought (CoT) Prompting**: Instruct the Vision model to "think step-by-step" (e.g., "Step 1: Locate the Rx symbol. Step 2: Read the first word next to it...").
2.  **Multi-Prospective Parsing**: Run the image through 3 different settings (Original, High-Contrast, Grayscale) and take the **Consensus Result**.
3.  **Pharmacology Check**: If the AI is unsure about a word (e.g., "Am-xi-llin"), it should cross-check against the OpenFDA database to find the closest valid drug match ("Amoxicillin").

## 🛠️ Phase 4: Human-in-the-Loop (Accuracy Shield)
*Goal: 0% Error Rate.*

1.  **Uncertainty Scoring**: If the AI has < 90% confidence in a word, highlight it in **Red** for the user.
2.  **Magnifier UI**: A tool that lets the user hover over a digitized word to see the original "messy" handwriting snippet for confirmation.
3.  **One-Tap Search**: "Did the AI get it wrong?" -> One-tap to search the FDA database for similar-sounding drugs.

---

> [!TIP]
> **Priority #1**: Implementing **Adaptive Sharpening** and **Pharmacology Consensus** will yield the biggest accuracy jump for blurry photos today.
