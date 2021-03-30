CXX=g++

CXXSRC=main.cpp graph.cpp csvreader.cpp sequence.cpp frames.cpp adjacency.cpp assignment.cpp adjacency3d.cpp correcthint.cpp framesscore.cpp fastareader.cpp
CXXOBJ=${CXXSRC:.cpp=.o}

CXXFLAGS=-O3 -std=c++11 -static
LDFLAGS=

graph-core: ${CXXOBJ}
	${CXX} ${LDFLAGS} -o $@ ${CXXOBJ}


clean:
	rm -f *.o graph-core
