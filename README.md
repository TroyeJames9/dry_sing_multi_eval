

# dry_sing_multi_eval

Five-Dimensional Acapella Singing Evaluation System based on funASR, include pronunciation, pitch accuracy, rhythm, fluency, and emotion."

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />

<p align="center">
  <a href="https://github.com/TroyeJames9/speech_recognition/">
  </a>
  <p align="center">
    <br />
    <a href="https://www.mubu.com/doc/5ZN7PfUKD9Y"><strong>Explore the doc of this project »</strong></a>
    <br />
    <br />
    <a href="https://github.com/TroyeJames9/dry_sing_multi_eval/blob/main/jupyter/funasr_run_single.ipynb">Start demo</a>
    ·
    <a href="https://github.com/TroyeJames9/dry_sing_multi_eval/issues">Report bug</a>
    ·
    <a href="https://github.com/TroyeJames9/dry_sing_multi_eval/issues">Propose new features</a>
    ·
    <a href="https://github.com/TroyeJames9/dry_sing_multi_eval/releases/">Stable release</a>
  </p>

</p>


 This README.md is for developers and users
 
## catalog

- [Get Start](#Get_Start)
  - [Pre-development configuration requirements](#Pre-development_configuration_requirements)
  - [Usage](#Usage)
- [Directory structure](#Directory_structure)
- [How to contribute](#How_to_contribute)
  - [How to Contribute to Open Source Projects](#How_to_Contribute_to_Open_Source_Projects)

### Get Start

###### **Pre-development configuration requirements**

1. **Python Version:** This project requires Python 3.x. recommend python 3.8
2. **Package Dependencies:** You can find the list of required packages in the requirements.txt file. Run `pip install -r requirements.txt` in terminal Located in the project root directory to install.Please note that this project also requires manual installation of the required versions of PyTorch as specified in the requirements.txt file. The default version is 1.8.2, and the version should not be greater than or equal to 2.x.x.
3. **Development Environment:** Set up your development environment with your preferred code editor or IDE. However, some imports in this project rely on the "source root" setting in PyCharm. It is recommended to use PyCharm for optimal functionality.In PyCharm, it is necessary to set `dry_sing_multi_eval/script` as the source root to ensure that the scripts run correctly.
4. **Access to Resources:** Due to the sensitive nature of the audio dataset used in this project, it cannot be publicly disclosed.samples in the `audio/qilai` are provided.If you intend to use this project with publicly available datasets, please ensure that the format of the input data matches the requirements of the scoring system. The required format for input data is as follows (TODO).
5. **Additional Dependencies:** This project utilizes pydub, thus requiring the installation of ffmpeg as well. It is recommended to install a version of ffmpeg that is newer than the December 21st, 2023 release.

###### **Usage**

1. To verify that the development environment is properly configured and to understand the design philosophy of this project, you can run `get_start.ipynb` in Jupyter Lab. This script is designed to demonstrate the functionality of the system and provide insights into its design principles.
2. TODO

### Directory structure

```
filetree 
├── audio/ 
│  ├── /{dataset_name}/
│  │  ├── example.wav
├── data/
├── eigen_json/ # dimensional data of each song Rhythm and notes.
├── jupyter/ 
├── orderResult_example/ # Sample output results from different ASR algorithms.
├── script/
│  ├── /setting.py # All cross-file global variables are computed and assigned by this module.
│  ├── /preprocess/ 
│  │  ├── funasr_go.py
│  │  └── ...
│  ├── /result/
│  │  ├── dataframe_op.py
├── resultJson/ # JSON of ASR recognition results.
├── test_space/ # Test script scaffold.
├── requirements.txt
├── style_guide.py # Style Guide Example for the Project

```

### How to contribute

Please read the [doc](https://www.mubu.com/doc/5ZN7PfUKD9Y) to understand the project guidelines, and develop according to the project standards before submitting a pull request (PR).

#### How to Contribute to Open Source Projects

Contributions make the open-source community an excellent place for learning, inspiration, and creativity. Thank you very much for any contributions you make.


1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Copyright

The project is licensed under the GNU License. Please refer to the [LICENSE.txt](https://github.com/TroyeJames9/dry_sing_multi_eval/LICENSE.txt) for details. 

<!-- links -->
[your-project-path]:TroyeJames9/dry_sing_multi_eval
[contributors-shield]: https://img.shields.io/github/contributors/TroyeJames9/dry_sing_multi_eval.svg?style=flat-square
[contributors-url]: https://github.com/TroyeJames9/dry_sing_multi_eval/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/TroyeJames9/dry_sing_multi_eval.svg?style=flat-square
[forks-url]: https://github.com/TroyeJames9/dry_sing_multi_eval/network/members
[stars-shield]: https://img.shields.io/github/stars/TroyeJames9/dry_sing_multi_eval.svg?style=flat-square
[stars-url]: https://github.com/TroyeJames9/dry_sing_multi_eval/stargazers
[issues-shield]: https://img.shields.io/github/issues/TroyeJames9/dry_sing_multi_eval.svg?style=flat-square
[issues-url]: https://img.shields.io/github/issues/TroyeJames9/dry_sing_multi_eval.svg
[license-shield]: https://img.shields.io/github/license/TroyeJames9/dry_sing_multi_eval.svg?style=flat-square
[license-url]: https://github.com/TroyeJames9/dry_sing_multi_eval/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/shaojintian




