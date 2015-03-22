#!/usr/bin/env python
import os

OUTPUT = "/home/administrator/workdir/git_folder/crf_project/feat/src_DA/out_shaped.txt"

entities = set(['G#protein_substructure', 'G#carbohydrate', 'G#other_artificial_source',
                'G#DNA_domain_or_region', 'G#RNA_domain_or_region', 'G#DNA_family_or_group', 'G#other_name',
                'G#protein_complex', 'G#protein_domain_or_region', 'G#protein_molecule', 'G#RNA_molecule', 'NE',
                'G#inorganic', '(OR', 'G#nucleotide', 'G#RNA_family_or_group', 'G#RNA_N/A', 'G#virus',
                'G#multi_cell', 'G#cell_component', 'G#DNA_N/A', 'G#DNA_molecule', 'G#protein_subunit',
                'G#cell_type', 'G#polynucleotide', 'G#atom', 'G#mono_cell', 'G#DNA_substructure',
                'G#protein_N/A', 'G#amino_acid_monomer', 'G#tissue', 'G#lipid', 'G#protein_family_or_group',
                'G#RNA_substructure', 'G#other_organic_compound', '(AND', 'G#peptide', 'G#body_part',
                'G#cell_line'])


ENTITIES = set(['G#cell_component_E', 'G#DNA_family_or_group_M', 'G#cell_component_M',
                'G#other_artificial_source', 'G#DNA_family_or_group_E', 'G#body_part_E', 'G#body_part_B',
                'G#other_name', 'G#body_part_M', 'G#other_organic_compound_M', 'G#cell_type_M',
                'G#DNA_substructure', 'G#DNA_molecule_M', 'G#cell_line_E', 'G#protein_domain_or_region',
                'G#protein_molecule', 'G#DNA_molecule_B', 'G#DNA_molecule_E', 'G#cell_line_M',
                'G#other_organic_compound_B', 'G#DNA_family_or_group_B', 'G#RNA_N/A', 'G#DNA_domain_or_region_E',
                'G#DNA_domain_or_region_B', 'G#DNA_N/A', 'G#DNA_domain_or_region_M', 'G#other_name_E',
                'G#inorganic_M', 'G#inorganic_E', 'G#inorganic_B', 'G#tissue', 'G#cell_component_B',
                'G#carbohydrate_E', 'G#RNA_domain_or_region', 'G#nucleotide', 'G#carbohydrate_B',
                'G#carbohydrate_M', 'G#other_name_B', 'G#protein_N/A_B', 'G#protein_N/A_E', 'G#protein_N/A_M',
                'G#DNA_substructure_M', 'G#multi_cell_M', 'G#multi_cell_B', 'G#DNA_substructure_B',
                'G#DNA_substructure_E', 'G#multi_cell_E', 'G#protein_domain_or_region_E',
                'G#protein_domain_or_region_B', 'G#protein_domain_or_region_M', 'G#RNA_molecule',
                'G#other_organic_compound_E', 'G#RNA_molecule_M', 'G#RNA_molecule_B', 'G#RNA_molecule_E',
                'G#RNA_family_or_group', 'G#protein_complex_M', 'G#protein_molecule_E', 'G#protein_molecule_B',
                'G#cell_component', 'G#cell_line_B', 'G#protein_complex_E', 'G#protein_molecule_M',
                'G#protein_complex_B', 'G#tissue_B', 'G#protein_substructure_E', 'G#protein_substructure_B',
                'G#tissue_E', 'G#atom_B', 'G#protein_substructure_M', 'G#polynucleotide_E', 'G#tissue_M',
                'G#lipid_B', 'G#amino_acid_monomer', 'G#protein_subunit_E', 'G#lipid_E', 'G#protein_subunit_M',
                'G#lipid_M', 'G#RNA_family_or_group_E', 'G#peptide', 'G#RNA_family_or_group_B',
                'G#RNA_family_or_group_M', 'G#atom_M', 'G#protein_substructure', 'G#DNA_domain_or_region',
                'G#RNA_N/A_M', 'G#RNA_N/A_E', 'G#RNA_N/A_B', 'G#polynucleotide_B', 'G#nucleotide_M',
                'G#nucleotide_B', 'NE', 'G#nucleotide_E', 'G#atom_E', 'G#mono_cell', 'G#virus',
                'G#DNA_molecule', 'G#protein_subunit', 'G#protein_subunit_B', 'G#cell_type', 'G#polynucleotide',
                'G#mono_cell_E', 'G#mono_cell_B', '(OR_E', 'G#other_artificial_source_M',
                'G#other_artificial_source_B', 'G#mono_cell_M', 'G#protein_N/A', 'G#other_artificial_source_E',
                'G#lipid', 'G#RNA_domain_or_region_M', '(OR_M', '(OR_B', 'G#RNA_domain_or_region_B',
                'G#protein_family_or_group', 'G#RNA_domain_or_region_E', 'G#other_organic_compound',
                'G#peptide_B', 'G#peptide_E', 'G#peptide_M', 'G#protein_family_or_group_B',
                'G#protein_family_or_group_E', 'G#carbohydrate', 'G#protein_family_or_group_M', 'G#DNA_N/A_E',
                'G#polynucleotide_M', 'G#DNA_family_or_group', 'G#DNA_N/A_B', 'G#DNA_N/A_M', 'G#protein_complex',
                'G#amino_acid_monomer_B', 'G#amino_acid_monomer_E', 'G#amino_acid_monomer_M', 'G#other_name_M',
                'G#inorganic', 'G#virus_M', 'G#cell_type_E', 'G#virus_B', 'G#virus_E', 'G#cell_type_B',
                'G#multi_cell', '(AND_M', 'G#RNA_substructure', '(AND_E', '(AND_B', 'G#atom',
                'G#RNA_substructure_B', 'G#RNA_substructure_E', 'G#body_part', 'G#cell_line'])


def file2data(f):
    f = open(f, 'r')
    data = []
    sentence = []
    k = 0
    for line in f.readlines():
        if not line.strip():
            data.append(sentence)
            sentence = []
        else:
            sentence.append(line.strip().split())
    return data


def data2file(data):
    f = open(OUTPUT + 'new', 'w')
    for sentence in data:
        for line in sentence:
             f.write(" ".join(line) + "\n")
        f.write("\n")


def data2entities(data):
    suffixes = ['_B', '_M', '_E']
    entities = set()
    for sentence in data:
        for line in sentence:
            sentence, shape, entity = line
            for suff in suffixes:
                if entity.endswith(suff):
                    entities.add(entity[:-2])
                    break
            else:
                entities.add(entity)

def clean_entity(entity):
    add_suf = ""
    suffixes = ['_B', '_M', '_E']
    for suff in suffixes:
        if entity.endswith(suff):
            add_suf = suff
            entity = entity.replace(add_suf, "")

    if "dna" in entity.lower():
        return "".join(("DNA", add_suf))
    elif "rna" in entity.lower():
        return "".join(("RNA", add_suf))
    elif "protein" in entity.lower():
        return "".join(("protein", add_suf))
    elif entity == 'G#cell_type':
        return "".join(("cell_type", add_suf))
    elif entity == 'G#cell_line':
        return "".join(("cell_line", add_suf))
    else:
        return "NE"

def clean_data(data):
    cleaned_data = []
    cleaned_sentence = []
    for sentence in data:
        for line in sentence:
            sentence, shape, entity = line
            entity = clean_entity(entity)
            cleaned_sentence.append([sentence, shape, entity])
        cleaned_data.append(cleaned_sentence)
        cleaned_sentence = []
    return cleaned_data

def main():
    data = file2data(OUTPUT)
    print "got data"
    #data2entities(data)
    data = clean_data(data)
    print "clean data"
    data2file(data)
    print "file data"

if __name__ == "__main__":
    main()

