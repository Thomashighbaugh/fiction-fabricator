import hashlib  # We'll use hashlib for simple hashing
import ollama
from loguru import logger
from tenacity import retry, wait_fixed, stop_after_attempt
from classes import AppUsageException
import config

class EmbeddingManager:
    def __init__(self, llm_config): # Add llm_config parameter
        self.embeddings = {}
        self.llm_config = llm_config  # Store llm_config

    @retry(wait=wait_fixed(config.RETRY_WAIT), stop=stop_after_attempt(3))
    def _generate_embedding(self, text):
        try:
            response = ollama.embeddings(model="nomic-embed-text:latest", prompt=text)
            # Keep the embedding as a list
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise AppUsageException(f"Error generating embedding: {e}") from e

    def add_embedding(self, key, text):
        embedding = self._generate_embedding(text)
        if embedding is not None:
            self.embeddings[key] = embedding

    def _dot_product(self, vec1, vec2):
        if vec1 is None or vec2 is None:
            return 0  # Handle cases where embeddings weren't generated
        return sum(x * y for x, y in zip(vec1, vec2))

    def _magnitude(self, vec):
        if vec is None:
            return 0 # Handle cases where embeddings weren't generated
        return (sum(x**2 for x in vec))**0.5

    def _cosine_similarity(self, vec1, vec2):
        mag1 = self._magnitude(vec1)
        mag2 = self._magnitude(vec2)
        if mag1 == 0 or mag2 == 0:
            return 0  # Handle zero magnitudes to avoid division by zero
        return self._dot_product(vec1, vec2) / (mag1 * mag2)

    def retrieve_relevant_embeddings(self, query, top_n=3):
        query_embedding = self._generate_embedding(query)
        if query_embedding is None:
            return []

        similarity_scores = {}
        for key, embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarity_scores[key] = similarity

        sorted_keys = sorted(similarity_scores, key=similarity_scores.get, reverse=True)
        return [key for key in sorted_keys[:top_n] if key in self.embeddings]
