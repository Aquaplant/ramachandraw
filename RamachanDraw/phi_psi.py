from math import pi

from Bio.PDB import PDBParser, PPBuilder
from rich.console import Console
from rich.table import Table

console = Console(color_system='windows')


def get_ignored_res(pdb_file_path: str, ignore_pdb_warnings: bool = False) -> (dict, list, list, list):
    x, y, res_ignored, res_output = [], [], [], {}
    for model in PDBParser(PERMISSIVE=False, QUIET=ignore_pdb_warnings).get_structure(id=None, file=pdb_file_path):
        for chain in model:
            peptides = PPBuilder().build_peptides(chain)
            for peptide in peptides:
                for aa, angles in zip(peptide, peptide.get_phi_psi_list()):
                    residue = chain.id + ":" + aa.resname + str(aa.id[1])
                    res_output[residue] = angles

    for key, value in res_output.items():
        # Only get residues with both phi and psi angles
        if value[0] and value[1]:
            x.append(value[0] * 180 / pi)
            y.append(value[1] * 180 / pi)
        else:
            res_ignored.append((key, value))

    return res_output, res_ignored, x, y


def phi_psi(pdb_file, return_ignored: bool = False, print_ignored: bool = False, ignore_pdb_warnings: bool = False):
    if ignore_pdb_warnings:
        try:
            from Bio.PDB.PDBExceptions import PDBConstructionWarning
            from warnings import simplefilter
            simplefilter('ignore', PDBConstructionWarning)
        except ImportError:
            pass

    def start(fp: str):
        phi_psi_data, ignored_res, x, y = get_ignored_res(pdb_file_path=fp, ignore_pdb_warnings=ignore_pdb_warnings)

        # print ignored residue table
        if print_ignored:
            table = Table(title='Ignored residues')
            table.add_column('Aminoacid\nresidue', style='red')
            table.add_column('\u03C6-\u03C8\nangles', justify='center')
            for _ in ignored_res:
                table.add_row(_[0], str(_[1]))
            console.print(table)

        if return_ignored:
            return phi_psi_data, ignored_res
        else:
            return phi_psi_data

    output = []
    if isinstance(pdb_file, str):
        output = start(fp=pdb_file)
    elif isinstance(pdb_file, list):
        for file in pdb_file:
            output.append(start(fp=file))

    return output
