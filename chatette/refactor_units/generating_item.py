# coding: utf-8
"""
Module `chatette.refactor_units.generating_item`
Contains the abstract class representing every item in the AST (or in rules)
that are able to generate examples.
"""


from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass
from random import uniform, choice, sample
from copy import deepcopy

from chatette.utils import sample_indulgent
from chatette.refactor_units import add_example_no_dup


class GeneratingItem(with_metaclass(ABCMeta, object)):
    """
    Represents all items that are able to generate an example
    (i.e. a string with meta-information such as entities or intent information).
    Each possibility of string that this item can generate is called
    a possibility or an example.
    """
    def __init__(self, name, leading_space):
        self._name = name
        self.full_name = self._compute_full_name()

        self._leading_space = leading_space
        print("for " + self.full_name + " leading space: " + str(leading_space))

        self._total_nb_possibilities = None

        # Cache: can contain a certain number of exampels previously generated
        self._cached_examples = []
    @abstractmethod
    def _compute_full_name(self):
        """
        Computes and returns the full name of the current item,
        that can be then displayed to the user.
        This name can be found in `self.full_name` after `__init__` was executed.
        """
        raise NotImplementedError()
    
    def get_max_nb_possibilities(self):
        """
        Returns the number of possible examples this item can generate.
        Uses the cached number of possibilities, or computes it.
        """
        if self._total_nb_possibilities is None:
            self._total_nb_possibilities = self._compute_nb_possibilities()
        return self._total_nb_possibilities
    @abstractmethod
    def _compute_nb_possibilities(self):
        """Returns the number of possible examples this item can generate."""
        raise NotImplementedError()
    

    def generate_random(self, **kwargs):
        """
        Returns an example generated at random.
        Can use the cached examples in some cases (better performance).
        """
        # use cache with probability `len(cached)/nb_possibilities`
        if (
            uniform(0, 1) <= \
            float(len(self._cached_examples)) / float(self.get_max_nb_possibilities())
        ):
            return choice(self._cached_examples)
        example = self._generate_random_strategy()
        if self._leading_space:
            example.prepend(' ')
        return example
    @abstractmethod
    def _generate_random_strategy(self):
        """
        Strategy to generate one example at random without using the cache.
        Returns the generated example.
        """
        raise NotImplementedError()
    
    def generate_all(self):
        """
        Returns the list of all examples this item can generate.
        Can use the cached examples in some cases (better performance).
        Also sets up the cache if needed and fixes the count of possibilities.
        """
        if len(self._cached_examples) == self.get_max_nb_possibilities():
            return deepcopy(self._cached_examples)

        all_examples = self._generate_all_strategy()
        print("for " + self.full_name + " all ex: " + str(all_examples))
        if self._leading_space:
            for ex in all_examples:
                ex.prepend(' ')
        if len(self._cached_examples) == 0:
            # TODO don't cache it all in all cases
            self._cached_examples = deepcopy(all_examples)
            self._total_nb_possibilities = len(all_examples)
        return all_examples
    @abstractmethod
    def _generate_all_strategy(self):
        """
        Strategy to generate all possible examples without using the cache.
        Returns this list.
        """
        raise NotImplementedError()

    def generate_nb_possibilities(self, nb_possibilities):
        """
        Returns a list containing `nb_possibilities` examples,
        chosen at random in the set of all possible examples.
        Can use the cached examples in some cases (better performances).
        @pre: `nb_possibilites` >= 2 (otherwise call `generate_random`)
        """
        max_nb_possibilities = self.get_max_nb_possibilities()
        if nb_possibilities > max_nb_possibilities:
            nb_possibilities = max_nb_possibilities

        if len(self._cached_examples) >= max_nb_possibilities:
            return sample(self._cached_examples, nb_possibilities)
        if nb_possibilities < float(max_nb_possibilities) / 5.0:  # QUESTION: is 5 a good idea?
            return self._generate_n_strategy(nb_possibilities)
        return sample_indulgent(self.generate_all(), nb_possibilities)
    def _generate_n_strategy(self, n):
        """
        Strategy to generate `n` examples without using the cache.
        Returns the list of generated examples.
        @pre: `n` <= `self.get_max_nb_possibilities()`
        """
        # TODO wouldn't it be better with a set rather than a list?
        generated_examples = []
        loop_count = 0
        while len(generated_examples) < n:
            current_ex = self.generate_random()
            add_example_no_dup(generated_examples, current_ex)
            loop_count += 1
            if loop_count > 10*n:  # QUESTION is that a good idea?
                break
        return generated_examples

    # @abstractmethod
    # def short_description(self):
    #     raise NotImplementedError()
    # @abstractmethod
    # def get_template_description(self):
    #     """
    #     Returns a string that should be equal to the definition of the unit
    #     in the template files (i.e. a template string on one or several lines).
    #     """
    #     raise NotImplementedError()

    # @abstractmethod
    # def print_DBG(self):
    #     raise NotImplementedError()

    def print_DBG(self):
        print(str(self))
    def __str__(self):
        return "<" + self.full_name + ">"
    def __repr__(self):  # TODO TMP (for testing purposes)
        return str(self)
