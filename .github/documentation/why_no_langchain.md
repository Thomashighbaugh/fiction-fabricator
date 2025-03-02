> But why aren't you using Langchain to chain prompts together?

I tried, the below is my post-mortem assessment as to why it didn't work out for this project. First
let me take the time to express how impressed I am with the Langchain ecosystem and surrounding
community, from my use of it I can say it is a potent framework with all imaginable means of
integrating AI agents into the many workflows it stands ready to innovate and improve.

## Langchain Post-Mortem Assessment

Langchain is a powerful library for orchestrating complex language model workflows, its abstractions and general-purpose design proved to be a less-than-ideal fit for this particular fiction fabrication project. The application's core workflow, while involving chained prompts and iterative refinement, followed a relatively straightforward "iterate-self-critique-answer" pattern akin to a SmartGPT-like approach. Langchain, designed for much broader and more intricate scenarios, introduced unnecessary layers of abstraction and complexity that ultimately became overhead. This overhead manifested in a noticeable slowdown of the application, as the library's machinery processed and managed workflows that were simpler than its intended use case.

Furthermore, the project's specific needs for prompt chaining and data handling were quite tailored. Interacting directly with the Ollama instance through native function calls and crafting prompts directly in Python code allowed for a much leaner and more optimized implementation. This direct approach eliminated the intermediary Langchain components, resulting in faster response times and a more streamlined application flow. By trading the generalized capabilities of Langchain for a more focused, native implementation, the project gained significant performance improvements and a codebase that is more directly aligned with its specific functional requirements, proving that sometimes, simpler is indeed better, especially when performance is a key consideration running on a laptop GPU instance of Ollama. Simpler, in this case also implies more directly optimized for the scenario, which anyone who is familiar with using Apple haardware is aware of how there is something to be said about when software is tightly optimized to the hardware it is running on.

### No Frameworks on the Horizon

For this project, I cannot foresee there being additional benefit to using any other framework in
LangChain's place as it would likely yield similar results. I will remain open to them, surely
anything to make my life easier (if it indeed will do so) but I think the narrow focus on high
quality, long-form text generation and focusing on improving the quality of the prompts and how they
are chained together will be the better investment of energy for this particular project.
