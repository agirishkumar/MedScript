import nltk
nltk.download('wordnet')
from nltk.translate.bleu_score import corpus_bleu
from nltk.translate.meteor_score import single_meteor_score
import evaluate
rouge = evaluate.load("rouge")


def calculate_bleu(references, candidates, weights):
  """
  Calculate the BLEU score for a set of candidate translations against reference translations.

  Args:
      references (List[str]): A list of reference translations.
      candidates (List[str]): A list of candidate translations to be evaluated.
      weights (Tuple[float]): A tuple of weights for unigrams, bigrams, etc., used to compute the BLEU score.

  Returns:
      float: The BLEU score representing the quality of the candidate translations.
  """
  tokenized_candidates = [text.split() for text in candidates]
  tokenized_references = [[text.split()] for text in references]

  bleu_scores = corpus_bleu(tokenized_references, tokenized_candidates, weights = weights)
  return bleu_scores
  
def calculate_rouge(references, candidates):
  """
  Calculate the ROUGE score for a set of candidate translations against reference translations.

  Args:
      references (List[str]): A list of reference translations.
      candidates (List[str]): A list of candidate translations to be evaluated.

  Returns:
      Dict: A dictionary containing the ROUGE scores.
  """
  
  return rouge.compute(predictions=candidates, references=references)

def calculate_meteor(references, candidates):
    """
    Calculate the METEOR score for a set of candidate translations against reference translations.

    Args:
        references (List[str]): A list of reference translations.
        candidates (List[str]): A list of candidate translations to be evaluated.

    Returns:
        float: The METEOR score representing the quality of the candidate translations.
    """
    scores = [single_meteor_score(ref.split(), hyp.split()) for ref, hyp in zip(references, candidates)]
    return sum(scores)/len(scores)

def jaccard_similarity(reference, generated):
    """
    Calculate the Jaccard similarity between a reference text and a generated text.

    The Jaccard similarity is defined as the size of the intersection divided by
    the size of the union of two sets of tokens derived from the input strings.

    Args:
        reference (str): The reference text to compare against.
        generated (str): The generated text to be evaluated.

    Returns:
        float: The Jaccard similarity score, ranging from 0 to 1, where 0 indicates
        no similarity and 1 indicates identical sets of tokens.
    """
    generated_tokens = set(generated.split())
    reference_tokens = set(reference.split())
    intersection = len(generated_tokens & reference_tokens)
    union = len(generated_tokens | reference_tokens)
    return intersection / union if union > 0 else 0
  
def calculate_jaccard_similarity(references, candidates):
  """
  Calculate the average Jaccard similarity between a list of reference texts and a list of generated texts.

  Args:
      references (List[str]): A list of reference texts to compare against.
      candidates (List[str]): A list of generated texts to be evaluated.

  Returns:
      float: The average Jaccard similarity score, ranging from 0 to 1, where 0 indicates
      no similarity and 1 indicates identical sets of tokens.
  """
  scores = [jaccard_similarity(references[i], candidates[i]) for i in range(len(references))]
  return sum(scores)/len(scores)

def evaluate_metrics(references, candidates, bleu_weights=(0.2, 0.3, 0.5)):
  """
  Evaluate the quality of the generated text against a set of reference texts using a
  variety of metrics.

  Args:
      references (List[str]): A list of reference texts to compare against.
      candidates (List[str]): A list of generated texts to be evaluated.
      bleu_weights (Tuple[float]): A tuple of weights to use when computing BLEU scores
          for each level of n-gram. Defaults to (0.2, 0.3, 0.5) for the standard
          BLEU-3 score.

  Returns:
      Dict[str, float]: A dictionary mapping the names of the evaluation metrics to
          their respective scores. The dictionary will contain the following keys:

              * bleu: The BLEU score computed using the specified weights.
              * meteor_score: The METEOR score.
              * jaccard_similarity: The Jaccard similarity between the reference and
                  generated texts.
              * rouge1: The ROUGE-1 score.
              * rouge2: The ROUGE-2 score.
              * rougeL: The ROUGE-L score.
              * rougeLsum: The ROUGE-Lsum score.
  """
  results = {
      'bleu': calculate_bleu(references, candidates, bleu_weights),
      'meteor_score': calculate_meteor(references, candidates),
      'jaccard_similarity': calculate_jaccard_similarity(references, candidates)
  }
  results.update(calculate_rouge(references, candidates))
  return results