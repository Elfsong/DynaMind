# Evaluations and Benchmarks
To assess the effectiveness of DynaMind in the context of continual learning, we devised three benchmark datasets: *Knowledge-driven Complex Reasoning*, *Knowledge Credibility Perception*, and *Knowledge Manipulation*. Subsequently, we conducted a series of quantitative analyses on these datasets, comparing the performance of a variety of LLMs within the DynaMind framework across these three distinct datasets.

## Knowledge-driven Complex Reasoning
The hallucinations that frequently arise in LLMs during complex reasoning tasks present a significant challenge in achieving convincing results[^azamfirei2023hallucinations]. Additionally, these models often struggle to provide a comprehensive and accurate reasoning process[^wang2022self]. In light of these issues, our objective with DynaMind is to incorporate memory capabilities into LLMs, enabling it to store the reasoning process and relevant knowledge in short-term memory. By doing so, DynaMind can employ heuristic strategies to break down complex problems into more manageable sub-problems and retain the solutions to these sub-problems in its short-term memory. Subsequently, it integrates the results from all the sub-problems to derive a conclusive outcome supported by a complete reasoning chain. Furthermore, by recalling pertinent knowledge from memory during the sub-problem reasoning process, DynaMind effectively mitigates the potential for hallucinations caused by insufficient knowledge in LLMs.

We selected a set of 200 high-quality complex knowledge-driven reasoning question-answer pairs from the ComplexWebQA dataset[^talmor2018web]. Table 1 reports the performance of different LLMs on this dataset. In the situation without external resources, Falcon achieved the best results with an accuracy of 17.5 %, whereas OpenAI GPT-4 substantially improved the accuracy to 92.5 % when utilizing the power of DynaMind.

| Model Name     | Basic      | DynaMind               |
| -------------- | ---------- | ---------------------- |
| OpenAI GPT-3.5 | 8.5        | 89.0 (+80.5)           |
| OpenAI GPT-4   | 16.0       | 92.5 (+76.5)           |
| Falcon-40B     | 17.5       | 85.0 (+67.5)           |
| Llama-30B      | 6.0        | 56.5 (+50.5)           |

Table 1: *Accuracy on Knowledge-driven Reasoning.*

## Knowledge Credibility Perception
The knowledge retained in long-term memory may become conflicting or obsolete over time. Identifying and upgrading such knowledge manually can be a strenuous and time-consuming process[^jiang2016timekg]. Consequently, we conceived a task to determine how DynaMind could automatically assess the trustworthiness of each piece of information in long-term memory within various contexts.

To quantitatively gauge this capability, we selected 200 unique statements from the SciFact dataset[^wadden2020fact]. Initially, we generated a counterfactual statement for each original statement using OpenAI GPT-4. Both of these statements were stored in long-term memory with identical initial credit scores. We then converted the original statements into question-answer pairs and prompted DynaMind to respond to these questions. After several cycles of the knowledge metabolism process, the credibility of the original statements is expected to increase, while the credibility of the constructed statements should correspondingly decay. Table 2 depicts the final ratio of original knowledge in the long-term memory after various epochs of knowledge metabolism, where the credibility of the original statement surpasses that of the counterfactual ones. It's worth noting that Falcon-40B demonstrated comparable performance to GPT-4 but with a four times smaller model size.

| Model Name     | 3 epochs  | 5 epochs  |
| -------------- | --------- | --------- |
| OpenAI GPT-3.5 | 48.5      | 61.5      |
| OpenAI GPT-4   | 79.0      | 84.5      |
| Falcon-40B     | 72.5      | 78.0      |
| Llama-30B      | 23.0      | 42.5      |

Table 2: *Performance on Credibility Perception.*

## Knowledge Manipulation
DynaMind equips language models with the ability to assimilate new knowledge without the modification of their parameters, which ensures models are adaptive amidst a perpetually evolving environment. In this section, we evaluated the capability of DynaMind to handle knowledge from three aspects: creation, update, and deletion.

For the creation aspect, we extracted 200 news as knowledge from the latest WikiNews 2023 archive[^Wikinews] (to ensure that the knowledge does not exist in LLMs). In terms of updating or erasing knowledge, we picked 200 questions from WebQuestions[^berant2013webquestion] as knowledge that the language model can correctly answer without additional knowledge (to ensure that the knowledge exists in LLMs). Following this, all acquired knowledge is added to DynaMind's long-term memory. We employed GPT-4 to produce a question-and-answer pair for each unit of knowledge, and then prompted DynaMind to generate the corresponding answer. The answer accuracy of different models in DynaMind is recorded in Table 3. A higher score indicates a robust capacity for continuous assimilation of new knowledge for creation and update indicators, whereas a lower score is more desirable for deletion tasks. GPT-4 possesses advantages in both knowledge creation and update tasks. However, it is noteworthy to mention that Falcon has outperformed GPT-4 in the deletion task, yielding the most impressive results.

| Model Name     | Create    | Update     | Delete    |
| -------------- | --------- | ---------- | --------- |
| OpenAI GPT-3.5 | 92.0      | 81.0       | 71.5      |
| OpenAI GPT-4   | 95.5      | 85.0       | 71.5      |
| Falcon-40B     | 90.5      | 83.5       | 74.0      |
| Llama-30B      | 88.0      | 78.5       | 70.0      |

Table 3: *Performance on Knowledge Manipulation.* 

[^azamfirei2023hallucinations]: Refer to specific citation
[^wang2022self]: Refer to specific citation
[^talmor2018web]: Refer to specific citation
[^jiang2016timekg]: Refer to specific citation
[^wadden2020fact]: Refer to specific citation
[^Wikinews]: Refer to specific citation
[^berant2013webquestion]: Refer to specific citation

> Please replace "Refer to specific citation" with the specific resource's information you are using. In Markdown, you reference a citation at the desired point in the text (like this[^1]), and then you can provide the citation information in a list at the end of the document. Replace "azamfirei2023hallucinations", "wang2022self", "talmor2018web", "jiang2016timekg", "wadden2020fact", "Wikinews", and "berant2013webquestion" with the full citation details. It's crucial to preserve the consistency between the reference in the body text and the citation list.
