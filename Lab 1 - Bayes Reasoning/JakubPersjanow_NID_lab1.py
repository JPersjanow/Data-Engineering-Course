import yaml, sys, glob, os


class YamlReader:
    """
    Yaml files reader
    """
    def __init__(self):
        self.filename = self.get_filename()
        self.content = self.open_yaml_file()

    def get_filename(self) -> str:
        """
        Method for getting all files with yaml extension in directory.
        :return:
        """
        yaml_files_in_dir: list = glob.glob("*.yaml")

        print("Available yaml files:")
        for index, yaml_file in enumerate(yaml_files_in_dir):
            print(f"[{index}] {yaml_file}")

        chosen = True

        while chosen:
            print("Which one to parse?")
            chosen_file_index: str = input()

            try:
                print(f"You have chosen: {yaml_files_in_dir[int(chosen_file_index)]}, is it correct? (Y/N)")
                answer: str = input()

                if answer == 'Y':
                    chosen = False
                elif answer == 'N':
                    continue
                else:
                    print(f"Cannot accept {answer} as proper answer!")

            except IndexError:
                print(f"File with index {chosen_file_index} not available!")

        return yaml_files_in_dir[int(chosen_file_index)]

    def open_yaml_file(self) -> dict:
        """
        Method for returning contents of yaml file.
        :return:
        """
        with open(self.filename, 'r', encoding='utf8') as yaml_file:
            content = yaml.safe_load(yaml_file)

        return content


class BayesCalculator:
    def __init__(self, yaml_file_content):
        """
        Bayes Calculator. Class for calculating probability of hypothesis under several facts.

        :param yaml_file_content: content from prepared yaml file.
        """
        self.yaml_content = yaml_file_content
        self.hypothesis, self.facts = self.gather_facts_and_hypothesis(content=self.yaml_content)
        self.check_content()
        self.pr_f = {}
        self.pr_h_f = []
        self.pr_h = []
        self.several_facts = None
        self.pr_h_fi = []

    def check_content(self) -> None:
        """
        Method for checking if given content is not empty.
        :return:
        """
        if not self.hypothesis or not self.facts:
            print("No data in Hypothesis or facts! Exiting.")
            sys.exit(1)

    @staticmethod
    def gather_facts_and_hypothesis(content):
        """
        Method for spliiting aquired yaml content into hypothesis and facts.
        :param content:
        :return:
        """
        for key, value in content.items():
            if key == 'Hypotheses':
                hypothesis = value
            elif key == 'Facts':
                facts = value
            else:
                print(f"Key {key} not recognized!")
        return hypothesis, facts

    def print_prob_a_priori(self) -> None:
        """
        Method for printing probability of hypothesis.
        :return:
        """
        print("Hypothesis: Probability a Priori P(h)")
        print("HYPOTHESIS, PROBABILITY (1/100%)")
        for i in self.hypothesis:
            print(f"{i['name']} : {i['prob']}")
        print("")

    def print_prob_f(self) -> None:
        """
        Method of printing probability of fact under hypothesis.
        :return:
        """
        print("Probability of facts P(F)")
        print("FACT, PROBABILITY (1/100%)")
        for key, value in self.pr_f.items():
            print(f"{key}, {value}")
        print("")

    def print_prob_a_prasteriori(self) -> None:
        """
        Method for printing probability of hypothesis under given facts.
        :return:
        """
        print("Hypothesis: Probability a Prasteriori P(h|F)")
        print("FACT, HYPOTHESIS, PROBABILITY (1/100%)")
        for i in self.pr_h_f:
            print(*i, sep=', ')

    def print_prob_h_fi(self):
        """
        Method for printing probability of hypothesis under several facts.
        :return:
        """
        print("Probability of several chosen facts P(h|Fi)")
        print("HYPOTHESIS, FACTS [FACT1, FACT2, ...], PROBABILITY (1/100%)")
        for prob in self.pr_h_fi:
            print(*prob, sep=', ')

    def get_prob_a_priori_list(self) -> list:
        """
        Method for getting hypothesis probability as a list of floats.
        :return:
        """
        list_ret = []
        for i in self.hypothesis:
            list_ret.append(i['prob'])
        self.pr_h = list_ret
        return list_ret

    def calculate_facts_probability(self) -> None:
        """
        Method for calculating facts probability.
        :return:
        """
        print("Calculating probability of facts Pr(F)")
        for fact in self.facts:
            print(f"Calculating for {fact['name']}")
            sum = 0.0
            for pr_h, pr_f_h in zip(self.get_prob_a_priori_list(), fact['prob']):
                sum += pr_h * pr_f_h
            self.pr_f[fact['name']] = round(sum, 5)
        print("")
        self.print_prob_f()

    def calculate_prob_a_posteriori(self) -> None:
        """
        Method for calculating probability of hypothesis under certain fact.
        :return:
        """
        print("Calculating probability a prasteriori P(h|F)")
        for fact in self.facts:
            for index, pr_f_h in enumerate(fact['prob']):
                pr_h_f = (pr_f_h * self.hypothesis[index]['prob']) / self.pr_f[fact['name']]
                self.pr_h_f.append([fact['name'], self.hypothesis[index]['name'], round(pr_h_f, 5)])
        print("")
        self.print_prob_a_prasteriori()

    def get_several_facts_numbers(self) -> list:
        """
        Method for acquiring facts from user.
        :return:
        """
        available_indexes = []
        ok = False
        while not ok:
            print("Facts to choose:")
            for index, fact in enumerate(self.facts):
                available_indexes.append(str(index))
                print(f"[{index}] {fact['name']}")

            print("Please insert facts numbers separated by space")
            st_chosen_facts = input()
            chosen_facts = st_chosen_facts.split(' ')
            ok = all(item in available_indexes for item in chosen_facts)

        return chosen_facts

    def prepare_chosen_facts(self) -> list:
        """
        Method for preparing only facts chosen by user.
        :return:
        """
        chosen_facts = self.get_several_facts_numbers()
        prepared_facts = []
        for i in chosen_facts:
            prepared_facts.append(self.facts[int(i)])

        return prepared_facts

    def calculate_several_facts(self):
        """
        Method for calculating probability of hypothesis under several facts.
        :return:
        """
        print("Calculating probability for several chosen facts P(h|Fi)")
        chosen_facts = self.prepare_chosen_facts()
        denominator = 0

        for index, h_prob_value in enumerate(self.get_prob_a_priori_list()):
            product_de = 1
            for fact in chosen_facts:
                product_de = product_de * fact['prob'][index]
            denominator += h_prob_value * product_de

        for index, h_prob_value in enumerate(self.get_prob_a_priori_list()):
            numerator = 0
            product_nu = 1

            for fact in chosen_facts:
                product_nu = product_nu * fact['prob'][index]
            numerator += h_prob_value * product_nu

            self.pr_h_fi.append([self.hypothesis[index]['name'], [d['name'] for d in chosen_facts], round(numerator / denominator)])
        print("")
        self.print_prob_h_fi()

if __name__ == '__main__':
    reader = YamlReader()
    bayes_cal = BayesCalculator(reader.content)
    bayes_cal.print_prob_a_priori()
    bayes_cal.calculate_facts_probability()
    bayes_cal.calculate_prob_a_posteriori()
    bayes_cal.calculate_several_facts()
