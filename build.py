#!/usr/bin/env python
import ast
import os
import re
import sys
from collections import defaultdict
from distutils.version import StrictVersion
from glob import glob
from shutil import rmtree, copyfile
from tempfile import mkdtemp

import autopep8
import click as cl
from inflection import camelize

GENERATE_COMMAND_TPL = 'java -jar %(jar)s generate -i %(host)s -l python -o %(tmpdir)s 1>/dev/null'
ATTUNE_API_URL = 'https://api-west1.attune.co/api-docs'
CODEGEN_URL = 'https://github.com/swagger-api/swagger-codegen'

PEP8OPTIONS = autopep8.parse_args(['', '-aa'])


def version(filename):
    if re.search('[\d+\.]+', filename):
        return (StrictVersion(re.search('[\d+\.]+', filename).group(0).strip('.')), filename)

    return False


class PyTransformer(ast.NodeTransformer):
    def __init__(self, filename):
        self.filename = filename
        self.basename = os.path.basename(filename)
        self.source = open(filename).read()
        self.classes = []

    def visit_ClassDef(self, node):
        if self.basename.endswith('.py'):
            new_class_name = camelize(self.basename[0:-3])

            if new_class_name != node.name:
                cl.secho('    > Replacing class name %s => %s' % (node.name, new_class_name), fg='blue')

                self.source = re.sub('(class\s+)%s' % node.name, '\\1%s' % new_class_name, self.source)
                node.name = new_class_name

        self.classes.append(node.name)


def build(*args):
    cwd = os.path.abspath(os.path.dirname(__file__))
    cl.secho('Changing current directory to %s' % cwd, fg='green')
    os.chdir(os.path.dirname(__file__))

    cl.secho('Looking for "swagger-codegen*.jar" in modules folder', fg='green')
    jar = glob('modules/swagger-codegen*.jar')
    for x in jar:
        cl.secho('  - %s' % x, fg='blue')

    if not jar:
        cl.secho('Not found JAR files in modules folder. Please download JAR from %s' % CODEGEN_URL, fg='red')

        raise SystemExit()

    versions = list(version(x) for x in jar if version(x))
    if not versions:
        jar = jar[0]
    else:
        jar = sorted(versions, key=lambda x: x[0])[-1][1]

    cl.secho('Using %s to generate code' % jar, fg='green')

    CMD_PARAMS = {
        'jar': jar,
        'host': ATTUNE_API_URL,
        # 'tpldir': 'swagger-templates/',
    }

    cl.secho('Creating swagger project temp directory', fg='green')
    CMD_PARAMS['tmpdir'] = tmpdir = mkdtemp('attune')
    cl.secho('  - %s' % tmpdir, fg='blue')
    try:
        CMD = GENERATE_COMMAND_TPL % CMD_PARAMS
        CMD += ' 2>/dev/null'

        # generating api library code with swagger
        cl.secho('Running swagger tool', fg='green')
        cl.secho('  - %s' % CMD, fg='blue')
        os.system(CMD)

        # processing generated code
        process = (
            {
                'label': 'models',
                'src': list(x for x in glob('%s/swagger_client/models/*.py' % tmpdir) if not x.endswith('__init__.py')),
                'dst': os.path.join('attune', 'client', 'model')
            }, {
                'label': 'api',
                'src': list(x for x in glob('%s/swagger_client/apis/*.py' % tmpdir) if not x.endswith('__init__.py')),
                'dst': os.path.join('attune', 'client', 'api'),
                'rewrite': {'fix_this_api.py': 'entities.py'},
                'add_oauth_token': True
            }
        )
        process_files = []

        for parsed in process:
            cl.secho('Copying generated %s files' % parsed['label'], fg='green')
            rewrite = parsed.get('rewrite', {})

            for fname in parsed['src']:
                dst = os.path.join(parsed['dst'], rewrite.get(os.path.basename(fname), os.path.basename(fname)))
                cl.secho('  - %s => %s' % (os.path.basename(fname), dst), fg='blue')
                copyfile(fname, dst)

                if parsed.get('add_oauth_token'):
                    cl.secho('    - Adding oauth_token to %s' % dst, fg='blue')

                    pysrc = open(dst).read()

                    pysrc = re.sub("( +)(all_params.append\('callback'\))",
                                   "\\1\\2\n\\1all_params.append('oauth_token')", pysrc)

                    pysrc = re.sub("( +)(callback=params.get\('callback'\))",
                                   "\\1\\2,\n\\1oauth_token=params.get('oauth_token')", pysrc)

                    file(dst, 'wb').write(pysrc)

                pysrc = open(dst).read()
                pysrc = pysrc.replace('api_client', 'client').replace('ApiClient', 'Client')

                if dst.endswith('ranking_params.py'):
                    # missed entitySource to model

                    cl.secho('    - Adding entitySource to RankingParams', fg='blue')

                    pysrc = pysrc.replace("'entity_type': 'str',", "'entity_type': 'str',\n'entity_source': 'str',")

                    pysrc = pysrc.replace("'entity_type': 'entityType',",
                                          "'entity_type': 'entityType',\n'entity_source': 'entitySource',")

                    pysrc = re.sub("( +)self._entity_type = None *\n",
                                   "\\1self._entity_type = None\n\\1self._entity_source = None\n", pysrc)

                    entity_type = re.search(' +@property\s+def entity_type\\(self\\):.*= entity_type *\n', pysrc,
                                            re.DOTALL)
                    if not entity_type:
                        cl.secho('    - Not found entity_type property setters/getters. Abort.', fg='red')
                        exit()

                    entity_type = entity_type.group(0)
                    entity_source = entity_type.replace('entity_type', 'entity_source')

                    pysrc = pysrc.replace(entity_type, entity_type + entity_source)

                file(dst, 'wb').write(pysrc)

                process_files.append(dst)

        if process_files:
            cl.secho('Processing files', fg='green')

            inits = defaultdict(list)

            for fname in process_files:
                # we do everything to avoid this, but we add this check to be sure
                if fname.endswith('__init__.py'):
                    continue

                cl.secho('  - %s' % fname, fg='blue')

                transformer = PyTransformer(fname)
                transformer.visit(ast.parse(transformer.source))
                file(fname, 'wb').write(transformer.source)

                for cls in transformer.classes:
                    inits[os.path.join(os.path.dirname(fname), '__init__.py')].append(
                            'from %s import %s' % (fname.replace('/', '.')[0:-3], cls)
                    )

            cl.secho('Updating __init__.py files', fg='green')
            for fname, imports in inits.iteritems():
                cl.secho('  - %s' % fname, fg='blue')

                source = ''
                if os.path.isfile(fname):
                    source = open(fname).read()

                for line in imports:
                    if line in source:
                        continue

                    source += '\n' + line

                source = autopep8.fix_code(str(source), PEP8OPTIONS)
                open(fname, 'w').write(source)
    finally:
        cl.secho('Removing temp directory', fg='green')
        rmtree(tmpdir)

    cl.secho('Processing models and api code with pep8', fg='green')
    files = glob('attune/client/model/*.py') + glob('attune/client/api/*.py')
    for fname in files:
        cl.secho('  - %s' % fname, fg='blue')

        source = open(fname).read()
        file(fname, 'w').write(autopep8.fix_code(source, PEP8OPTIONS))


if __name__ == '__main__':
    try:
        build(sys.argv)
    except SystemExit:
        pass
