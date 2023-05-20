"""
Inspired by https://github.com/stanford-crfm/helm/blob/0eaaa62a2263ddb94e9850ee629423b010f57e4a/src/helm/benchmark/scenarios/babi_qa_scenario.py
"""
import numpy as np
from collections import defaultdict
from lm_eval.base import rf, Task
from lm_eval.metrics import mean


_CITATION = """
@article{weston2015towards,
  title={Towards ai-complete question answering: A set of prerequisite toy tasks},
  author={Weston, Jason and Bordes, Antoine and Chopra, Sumit and Rush, Alexander M and Van Merri{\"e}nboer, Bart and Joulin, Armand and Mikolov, Tomas},
  journal={arXiv preprint arXiv:1502.05698},
  year={2015}
}
"""

class Babi(Task):
    VERSION = 0
    DATASET_PATH = "Muennighoff/babi"
    DATASET_NAME = None

    def has_training_docs(self):
        return True

    def has_validation_docs(self):
        return True

    def has_test_docs(self):
        return True

    def training_docs(self):
        if self.has_training_docs():
            return self.dataset["train"]

    def validation_docs(self):
        if self.has_validation_docs():
            return self.dataset["valid"]

    def test_docs(self):
        if self.has_test_docs():
            return self.dataset["test"]

    def doc_to_text(self, doc):
        return (
            doc['passage'] + doc['question']
        )

    def should_decontaminate(self):
        return False # TODO Necessary?

    def doc_to_decontamination_query(self, doc):
        return doc['passage'] + doc['question']

    def doc_to_target(self, doc):
        return " " + doc['answer']

    def construct_requests(self, doc, ctx):
        """Uses RequestFactory to construct Requests and returns an iterable of
        Requests which will be sent to the LM.

        :param doc:
            The document as returned from training_docs, validation_docs, or test_docs.
        :param ctx: str
            The context string, generated by fewshot_context. This includes the natural
            language description, as well as the few shot examples, and the question
            part of the document for `doc`.
        """
        return rf.greedy_until(ctx, ["\n"])

    def process_results(self, doc, results):
        """Take a single document and the LM results and evaluates, returning a
        dict where keys are the names of submetrics and values are the values of
        the metric for that one document

        :param doc:
            The document as returned from training_docs, validation_docs, or test_docs.
        :param results:
            The results of the requests created in construct_requests.
        """
        gold = doc["answer"]
        pred = gold.strip() == results[0].strip()
        return {"em": pred}

    def aggregation(self):
        return {
            "em": mean,
        }

    def higher_is_better(self):
        return {
            "em": True,
        }
