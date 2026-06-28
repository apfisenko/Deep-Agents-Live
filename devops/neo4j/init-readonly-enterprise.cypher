// Enterprise / Aura only — fine-grained RBAC (NOT supported in Community Edition).
// Run as admin after graph-up, substituting user/password or via cypher-shell params.
//
// CREATE ROLE text2cypher_reader;
// GRANT MATCH {*} ON GRAPH neo4j TO text2cypher_reader;
// GRANT SHOW INDEXES ON DBMS TO text2cypher_reader;
// GRANT SHOW CONSTRAINTS ON DBMS TO text2cypher_reader;
// CREATE USER text2cypher IF NOT EXISTS
//   SET PASSWORD '***'
//   CHANGE NOT REQUIRED;
// GRANT ROLE text2cypher_reader TO text2cypher;
