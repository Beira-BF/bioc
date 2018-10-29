import json

import jsonlines
from bioc.bioc import *
from bioc.constants import *


def parse_collection(obj: dict) -> BioCCollection:
    collection = BioCCollection()
    collection.source = obj['source']
    collection.date = obj['date']
    collection.key = obj['key']
    collection.infons = obj['infons']
    for doc in obj['documents']:
        collection.add_document(parse_doc(doc))
    return collection


def parse_annotation(obj: dict) -> BioCAnnotation:
    ann = BioCAnnotation()
    ann.id = obj['id']
    ann.infons = obj['infons']
    ann.text = obj['text']
    for loc in obj['locations']:
        ann.add_location(BioCLocation(loc['offset'], loc['length']))
    return ann


def parse_relation(obj: dict) -> BioCRelation:
    rel = BioCRelation()
    rel.id = obj['id']
    rel.infons = obj['infons']
    for node in obj['nodes']:
        rel.add_node(BioCNode(node['refid'], node['role']))
    return rel


def parse_sentence(obj: dict) -> BioCSentence:
    sentence = BioCSentence()
    sentence.offset = obj['offset']
    sentence.infons = obj['infons']
    sentence.text = obj['text']
    for annotation in obj['annotations']:
        sentence.add_annotation(parse_annotation(annotation))
    for relation in obj['relations']:
        sentence.add_relation(parse_relation(relation))
    return sentence


def parse_passage(obj: dict) -> BioCPassage:
    passage = BioCPassage()
    passage.offset = obj['offset']
    passage.infons = obj['infons']
    if 'text' in obj:
        passage.text = obj['text']
    for sentence in obj['sentences']:
        passage.add_sentence(parse_sentence(sentence))
    for annotation in obj['annotations']:
        passage.add_annotation(parse_annotation(annotation))
    for relation in obj['relations']:
        passage.add_relation(parse_relation(relation))
    return passage


def parse_doc(obj: dict) -> BioCDocument:
    doc = BioCDocument()
    doc.id = obj['id']
    doc.infons = obj['infons']
    for passage in obj['passages']:
        doc.add_passage(parse_passage(passage))
    for annotation in obj['annotations']:
        doc.add_annotation(parse_annotation(annotation))
    for relation in obj['relations']:
        doc.add_relation(parse_relation(relation))
    return doc


def load(fp, **kwargs) -> BioCCollection:
    """
    Deserialize fp (a .read()-supporting text file or binary file containing a JSON document) to a BioCCollection object

    Args:
        fp: a file containing a JSON document
        **kwargs:

    Returns:
        BioCCollection: a collection
    """
    obj = json.load(fp, **kwargs)
    return parse_collection(obj)


def loads(s: str, **kwargs) -> BioCCollection:
    """
    Deserialize s (a str, bytes or bytearray instance containing a JSON document) to a BioCCollection object.

    Args:
        s(str):
        **kwargs:

    Returns:
        BioCCollection: a collection
    """
    obj = json.loads(s, **kwargs)
    return parse_collection(obj)


class BioCJsonIterReader(object):
    def __init__(self, file: str, level: int):
        if level not in {DOCUMENT, PASSAGE, SENTENCE}:
            raise ValueError('Unrecognized level: %s' % level)

        self.reader = jsonlines.open(file)
        self.reader_iter = iter(self.reader)
        self.level = level

    def __iter__(self):
        return self

    def __next__(self):
        obj = next(self.reader_iter)
        if self.level == DOCUMENT:
            return parse_doc(obj)
        elif self.level == PASSAGE:
            return parse_passage(obj)
        elif self.level == SENTENCE:
            return parse_sentence(obj)

    def close(self):
        self.reader.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

