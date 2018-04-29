#!/usr/bin/python3
# Analysis to determine fault frequency and potential operators
import pandas
from jinja2 import Environment, FileSystemLoader

# Helper Function
def read_csv(file_path):
    with open(file_path) as f:
        data = pandas.read_csv(f)
    return data

def save_csv(file_path, df):
    with open(file_path, 'w') as f:
        df.to_csv(f)

def save_file_path(file_path):
    file_path_parts = file_path.split(".")
    return ".".join(file_path_parts[:-1]) + ".out." + file_path_parts[-1]

def jinja2_tex_escape(content):
    return str(content).replace("%", "\\%")

def jinja2_round_if_float(content, decimals):
    if isinstance(content, float):
        return round(content, decimals)
    return content

jinja2_custom_filters = {
    'tex_escape': jinja2_tex_escape,
    'round_if_float': jinja2_round_if_float
}

def make_resource(template, file_path, **args):
    jinja_env = Environment(loader=FileSystemLoader('templates/'))
    jinja_env.filters.update(jinja2_custom_filters)
    template = jinja_env.get_template(template)
    resource = template.render(**args)
    with open(file_path, 'w') as f:
        f.write(resource)

# Data set functions
def vigo_data_analysis(file_path):
    df = read_csv(file_path)
    df = df.sort_values('actual issues', ascending=False)
    df = df.drop(df[df["actual issues"] == 0].index)

    tp_cols = list(filter(lambda a: a is not None, [col if col[0:2] == 'tp' else None for col in list(df)]))
    df['all tp'] = sum([df[tp] for tp in tp_cols]) / len(tp_cols)

    fp_cols = list(filter(lambda a: a is not None, [col if col[0:2] == 'fp' else None for col in list(df)]))
    df['all fp'] = sum([df[fp] for fp in fp_cols]) / len(tp_cols)

    df['pct tp'] = df['all tp'] / df['actual issues']

    save_csv(
        save_file_path(file_path),
        df.filter([
            'Principle',
            'Guideline',
            'Sucess criteria',
            'level',
            'actual issues',
            'all tp',
            'pct tp',
            'all fp'
        ])
    )
    column_friendly_name = {
        'Sucess criteria': 'Success Criteria',
        'actual issues': 'Actual Issues',
        'all tp': 'True Positives',
        'all fp': 'False Positives'
    }
    make_resource("gen-table.tex.jinja2", "../figures/vigo-manual-analysis.tex",
                  data=df.filter(['Sucess criteria', 'actual issues', 'all tp', 'all fp']).rename(columns=column_friendly_name).head(6),
                  description="Mean results of testing conducted by Vigo (top 6 results)",
                  label="vigo-manual-analysis"
            )

# General functions
if __name__ == "__main__":
    vigo_data_analysis('../thirdparty/vigo-manual-analysis.csv')
