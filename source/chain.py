import os 

class ChainExecutor:

    def __init__(self, llm_connection):
        self.elements = []
        self.llm_connection = llm_connection

    def add_element(self, element: 'BaseChainElement') -> None:
        self.elements.append(element)

    def run(self) -> None:

        elements_to_execute = self.elements[::]

        while len(elements_to_execute) > 0:
            current_element = elements_to_execute.pop(0)
            current_element.step(self.llm_connection)
            while not current_element.is_done():
                # Make print light grey color.
                print("\033[0;37m", end="")

                current_element.step(self.llm_connection)

# Abstract class chain element.
class BaseChainElement:

    def is_done(self) -> bool:
        raise NotImplementedError
    
    def step(self, llm_connection) -> None:
        raise NotImplementedError
