// Baseline Theme-[:REQUIRES]->Theme edges (analysis.md §2, eval M2/M6)
// Idempotent MERGE — run after theme extraction.

MERGE (rag:Theme {canonicalName: 'RAG'})
SET rag.name = 'RAG', rag.aliases = coalesce(rag.aliases, []);

MERGE (adv:Theme {canonicalName: 'Advanced RAG'})
SET adv.name = 'Advanced RAG';

MERGE (graphrag:Theme {canonicalName: 'GraphRAG'})
SET graphrag.name = 'GraphRAG';

MERGE (vdb:Theme {canonicalName: 'Vector DB'})
SET vdb.name = 'Vector DB';

MERGE (hybrid:Theme {canonicalName: 'Hybrid Search'})
SET hybrid.name = 'Hybrid Search';

MERGE (langgraph:Theme {canonicalName: 'LangGraph agents'})
SET langgraph.name = 'LangGraph agents';

MERGE (tool:Theme {canonicalName: 'Tool calling'})
SET tool.name = 'Tool calling';

MERGE (multi:Theme {canonicalName: 'Multi-agent systems'})
SET multi.name = 'Multi-agent systems';

MERGE (mm:Theme {canonicalName: 'Multimodal RAG'})
SET mm.name = 'Multimodal RAG';

MERGE (mcp:Theme {canonicalName: 'MCP'})
SET mcp.name = 'MCP';

MATCH (a:Theme {canonicalName: 'Advanced RAG'}), (b:Theme {canonicalName: 'RAG'})
MERGE (a)-[:REQUIRES]->(b);

MATCH (a:Theme {canonicalName: 'GraphRAG'}), (b:Theme {canonicalName: 'Vector DB'})
MERGE (a)-[:REQUIRES]->(b);

MATCH (a:Theme {canonicalName: 'GraphRAG'}), (b:Theme {canonicalName: 'RAG'})
MERGE (a)-[:REQUIRES]->(b);

MATCH (a:Theme {canonicalName: 'Hybrid Search'}), (b:Theme {canonicalName: 'Vector DB'})
MERGE (a)-[:REQUIRES]->(b);

MATCH (a:Theme {canonicalName: 'LangGraph agents'}), (b:Theme {canonicalName: 'Tool calling'})
MERGE (a)-[:REQUIRES]->(b);

MATCH (a:Theme {canonicalName: 'Multi-agent systems'}), (b:Theme {canonicalName: 'LangGraph agents'})
MERGE (a)-[:REQUIRES]->(b);

MATCH (a:Theme {canonicalName: 'Multimodal RAG'}), (b:Theme {canonicalName: 'RAG'})
MERGE (a)-[:REQUIRES]->(b);

MATCH (a:Theme {canonicalName: 'MCP'}), (b:Theme {canonicalName: 'Tool calling'})
MERGE (a)-[:REQUIRES]->(b);
