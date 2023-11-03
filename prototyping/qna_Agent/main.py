import argparse
from prototyping.qna_Agent.src import dataProcessor, embed, QnA, summary

def process_data(args):
    if args.dataset:
        if args.url is None:
            raise ValueError("Error: When dataset is True, a URL must be provided.")

        print(f"-------start downloading data from the {args.url}-------")
        dataProcessor.DataProcessor(args.url)
        print(f"-------finish downloading data-------\n\n")

        print(f"-------start summarizing the texts-------")
        summary.save_summary()
        print(f"-------finish summarizing the texts-------\n\n")

        print(f"-------start embeddings the texts-------")
        embed.save_embeddings()
        print(f"-------finish embeddings the texts-------\n\n")
        
        return QnA.respond_to_context(args.question)
    else:
        return QnA.respond_to_context(args.question)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--question', type=str, required=True, help='A required question')
    parser.add_argument('--dataset', action='store_true', default=False, help='Flag indicating if there is no dataset')
    parser.add_argument('--url', type=str, nargs='?', default=None, help='URL for the data to be downloaded')
    return parser.parse_args()

def main():
    args = parse_arguments()
    result = process_data(args)
    print(result)

if __name__ == '__main__':
    main()
