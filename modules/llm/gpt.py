import openai

class GPT():
	"""
	Initialize the GPT class for interacting with OpenAI's GPT model.
	GPT provides basic methods for interacting with the model and parsing its output.
	"""

	def __init__(self, key: str, model: str = 'gpt-3.5-turbo-0613',
							 temperature: float = 0.7, keep_memory: bool = True):
		"""
		Initialize the LLM class. Private variables, denoted by double underscores, are not directly accessible from outside the class.
		:param key: OpenAI API key
		:param model: The model to use (default: gpt-3.5-turbo-0613)
		"""
		self._model = model  # Model to use, can be replaced with other models as needed (e.g., gpt-4 or longer-context gpt-3.5-turbo)
		self._openai_key = key  # Each LLM object should have a unique key for multithreading
		self._cost = 0  # Store the token consumption
		self._memories = []  # Current memories
		self._keep_memory = keep_memory  # Whether to retain memories (not needed for summarizers)
		self._temperature = temperature
		self._history = []

	def get_memories(self):
		return self._memories
	
	def get_history(self):
		return self._history

	def memories_update(self, role: str, content: str):
		""" 
		Update memories to set roles (system, user, assistant) and content, forming a complete memory.
		:param role: Role (system, user, assistant)
		:param content: Content
		:return: None
		"""
		if role not in ["system", "user", "assistant"]:
			raise ValueError(f"Unrecognized role: {role}")

		if role == "system" and len(self._memories) > 0:
			raise ValueError("System role can only be added when memories are empty")
		if role == "user" and len(self._memories) > 0 and self._memories[-1]["role"] == "user":
			raise ValueError("User role can only be added if the previous round was a system or assistant role")
		if role == "assistant" and len(self._memories) > 0 and self._memories[-1]["role"] != "user":
			raise ValueError("Assistant role can only be added if the previous round was a user role")
		self._memories.append({"role": role, "content": content})
		self._history.append({"role": role, "content": content})


	def generate_answer(self, input: str, try_times=0, **kwargs) -> str:
		"""
		Interact with the GPT model.
		:param input: prompt

		:param kwargs: Parameters to pass for conversation with the model, such as temperature, max_tokens, etc.
		:return: Text-based output result
		"""
		if not self._keep_memory:
				self._memories = [self._memories[0]]

		if try_times == 0:
			self._memories.append({"role": "user", "content": input})
			self._history.append({"role": "user", "content": input})
		else:
			if self._memories[-1]["role"] == "assistant":
				self._memories = self._memories[:-1]

		openai.api_key = self._openai_key

		try:
			response = openai.ChatCompletion.create(
				model=self._model,
				messages=self._memories,
				temperature=self._temperature,
			)
			self._cost += response['usage']["total_tokens"]
			content = response['choices'][0]['message']['content']
			self._memories.append({"role": "assistant", "content": content})
			self._history.append({"role": "assistant", "content": content})
			return content
		except Exception as e:
			raise ConnectionError(f"Error in generate_answer: {e}")
