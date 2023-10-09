import pathlib
import sys
working_dir = pathlib.Path(__file__).parent.__str__()
sys.path.append(working_dir)
import cy_vn_suggestion.suggestions
fx= cy_vn_suggestion.suggestions.suggest("Mot con vit xoe ra 2 cai canh")
print(fx)