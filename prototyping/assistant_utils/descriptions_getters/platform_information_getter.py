import logging
import os

import pandas as pd

from prototyping.qna_Agent import dataProcessor, summary, embed, QnA

class PlatformInformationGetter:
    ''' Abstract class defines interface to get information about services '''
    DATASET_PATH = "./prototyping/qna_Agent/data/dataset.csv"
    def __init__(self):
        if not os.path.exists(self.DATASET_PATH):
            self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
            repo_url = 'https://github.com/singnet/dev-portal/archive/refs/heads/master.zip'
            processor = dataProcessor.DataProcessor(repo_url)
            summary.save_summary()
            embed.save_embeddings()
        self.df = pd.read_csv(self.DATASET_PATH)

    def get_question_context(self, question):
        relevant_id = QnA.retrieve_answer_directory(question) - 1

        if relevant_id == -1:
            return None

        context = QnA.get_context(
            dataset=self.df, context_id=relevant_id, question=question)

        prompt = f"""using next information.\n
            ---------------------\n
            {context}\n
            ---------------------\n 
            answer the user's question"""
        return prompt
if __name__ == '__main__':
    getter = PlatformInformationGetter();
    print(getter.get_question_context("how To get the metamask plugin install?"))