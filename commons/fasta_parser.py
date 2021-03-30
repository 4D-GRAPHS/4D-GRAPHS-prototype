def get_protein_sequence_list(fasta_file, protein):
    lines = [line.strip() for line in open(fasta_file, 'r').readlines()]
    protname = [line.strip('>') for line in lines if line.startswith('>')][0]
    if protname.rstrip() != protein:
        raise (Exception("A fasta file protein name does not match the given protein name!"))
    return list(''.join([line.strip() for line in lines if not line.strip().startswith('>')]))
