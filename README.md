# Boyang Cheng's Portfolio Website

Personal portfolio website for Boyang Cheng: <https://cheng-boyang.github.io/>

A single static page (`index.html`) styled as an engraved book on manuscript paper. Each chapter fills one screen and the menu jumps between them.

## Updating content

- **Text:** edit the chapter sections in `index.html`.
- **Publications:** edit `assets/data/publications.json`, then run `make` in `cv/`. It updates the Reference chapter in `index.html` and the CV together.
- **Images:** chapter engravings are in `assets/images/chipmonk/`, die photos in `assets/images/chips/`.
- **CV:** LaTeX source in [`cv/`](cv/). Run `make` there to rebuild the PDF and refresh the publication lists on both the CV and the website.

## Using this as a template

You are welcome to use this design for your own site. Replace the personal content (text, CV, publications and photos) with your own, and please credit **Boyang Cheng** in your acknowledgements, README or footer.

## License

| What | License |
|---|---|
| Website template: design, HTML, CSS and JavaScript in `index.html` | [MIT](LICENSE). Keep the copyright notice and credit Boyang Cheng. |
| Images in `assets/images/`, including the engraved illustrations | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/): credit Boyang Cheng, non-commercial use only |
| Personal content: biography, CV, publication record | © Boyang Cheng, all rights reserved |

See [LICENSE](LICENSE) for the full terms.
