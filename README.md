

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
  </p>

</p>


 This README.md is for developers and users
 
## catalog

- [Get Start](#Get Start)
  - [Pre-development configuration requirements](#Pre-development_configuration_requirements)
  - [Usage](#Usage)
- [文件目录说明](#文件目录说明)
- [开发的架构](#开发的架构)
- [部署](#部署)
- [使用到的框架](#使用到的框架)
- [贡献者](#贡献者)
  - [如何参与开源项目](#如何参与开源项目)
- [版本控制](#版本控制)
- [作者](#作者)
- [鸣谢](#鸣谢)

### Get Start

###### **Pre-development configuration requirements**

1. **Python Version:** This project requires Python 3.x. recommend python 3.8
2. **Package Dependencies:** You can find the list of required packages in the requirements.txt file. Run `pip install -r requirements.txt` in terminal Located in the project root directory to install.Please note that this project also requires manual installation of the required versions of PyTorch as specified in the requirements.txt file. The default version is 1.8.2, and the version should not be greater than or equal to 2.x.x.
3. **Development Environment:** Set up your development environment with your preferred code editor or IDE. However, some imports in this project rely on the "source root" setting in PyCharm. It is recommended to use PyCharm for optimal functionality.In PyCharm, it is necessary to set `dry_sing_multi_eval/script` as the source root to ensure that the scripts run correctly.
4. **Access to Resources:** Due to the sensitive nature of the audio dataset used in this project, it cannot be publicly disclosed.samples in the `audio/qilai` are provided.If you intend to use this project with publicly available datasets, please ensure that the format of the input data matches the requirements of the scoring system. The required format for input data is as follows (TODO).

###### **Usage**

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo

```sh
git clone https://github.com/shaojintian/Best_README_template.git
```

### 文件目录说明
eg:

```
filetree 
├── ARCHITECTURE.md
├── LICENSE.txt
├── README.md
├── /account/
├── /bbs/
├── /docs/
│  ├── /rules/
│  │  ├── backend.txt
│  │  └── frontend.txt
├── manage.py
├── /oa/
├── /static/
├── /templates/
├── useless.md
└── /util/

```





### 开发的架构 

请阅读[ARCHITECTURE.md](https://github.com/shaojintian/Best_README_template/blob/master/ARCHITECTURE.md) 查阅为该项目的架构。

### 部署

暂无

### 使用到的框架

- [xxxxxxx](https://getbootstrap.com)
- [xxxxxxx](https://jquery.com)
- [xxxxxxx](https://laravel.com)

### 贡献者

请阅读**CONTRIBUTING.md** 查阅为该项目做出贡献的开发者。

#### 如何参与开源项目

贡献使开源社区成为一个学习、激励和创造的绝佳场所。你所作的任何贡献都是**非常感谢**的。


1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



### 版本控制

该项目使用Git进行版本管理。您可以在repository参看当前可用版本。

### 作者

xxx@xxxx

知乎:xxxx  &ensp; qq:xxxxxx    

 *您也可以在贡献者名单中参看所有参与该项目的开发者。*

### 版权说明

该项目签署了MIT 授权许可，详情请参阅 [LICENSE.txt](https://github.com/shaojintian/Best_README_template/blob/master/LICENSE.txt)

### 鸣谢


- [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
- [Img Shields](https://shields.io)
- [Choose an Open Source License](https://choosealicense.com)
- [GitHub Pages](https://pages.github.com)
- [Animate.css](https://daneden.github.io/animate.css)
- [xxxxxxxxxxxxxx](https://connoratherton.com/loaders)

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
[license-url]: https://github.com/TroyeJames9/dry_sing_multi_eval/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/shaojintian




