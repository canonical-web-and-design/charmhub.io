import hljs from "highlight.js/lib/core";
import python from "highlight.js/lib/languages/python";
import bash from "highlight.js/lib/languages/bash";
import "highlight.js/styles/github.css";

hljs.registerLanguage("python", python);
hljs.registerLanguage("bash", bash);

export { hljs };
