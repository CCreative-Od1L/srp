## 请安装前置依赖
from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
import json
## 安装完别忘了添加以下下面 todo 的参数
## 比较隐私的内容请做好保护


class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    # 创建节点
    def create_node(self, node_data):
        with self.driver.session(database="neo4j") as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = ""
            if( 'alias' in node_data['content']):
                result = session.execute_write(
                    self._create_node_with_alias, node_data['content']['type'], node_data['name'], node_data['content']['alias']
                )
            else:
                result = session.execute_write(
                    self._create_node_without_alias, node_data['content']['type'], node_data['name']
                )
            
            assert(result != "")
            for row in result:
                print("Created node: {node_name}".format(node_name=row['name']))

    @staticmethod
    def _create_node_with_alias(tx, node_type,node_name,node_alias):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = ()
        match node_type:
            case 'disease':
                query = (
                    "CREATE (p1: Disease { name: $node_name, alias: $node_alias }) "
                    "RETURN p1"
                )
            case 'chemical':
                query = (
                    "CREATE (p1: Chemical { name: $node_name, alias: $node_alias }) "
                    "RETURN p1"
                )
            case 'genetic':
                query = (
                    "CREATE (p1: Genetic { name: $node_name, alias: $node_alias }) "
                    "RETURN p1"
                )
            case 'treatment':
                query = (
                    "CREATE (p1: Treatment { name: $node_name, alias: $node_alias }) "
                    "RETURN p1"
                )
        assert(query != ())
        result = tx.run(query,node_name=node_name,node_alias=node_alias)
        try:
            return [{"name": row["p1"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _create_node_without_alias(tx, node_type,node_name):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = ()
        match node_type:
            case 'disease':
                query = (
                    "CREATE (p1: Disease { name: $node_name }) "
                    "RETURN p1"
                )
            case 'chemical':
                query = (
                    "CREATE (p1: Chemical { name: $node_name }) "
                    "RETURN p1"
                )
            case 'genetic':
                query = (
                    "CREATE (p1: Genetic { name: $node_name }) "
                    "RETURN p1"
                )
            case 'treatment':
                query = (
                    "CREATE (p1: Treatment { name: $node_name }) "
                    "RETURN p1"
                )
        assert(query != ())
        result = tx.run(query,node_name=node_name)
        try:
            return [{"name": row["p1"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    def find_node(self, node_data):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_person, node_data['content']['type'], node_data['name'])
            for row in result:
                print("Found person: {row}".format(row=row))
    #todo 要修改 node_type 不能为query参数 
    @staticmethod
    def _find_and_return_node(tx, node_type, node_name):
        # 执行语句
        query = (
            "MATCH (p: $node_type) "
            "WHERE p.name = $node_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, node_type=node_type, node_name=node_name)
        return [row["name"] for row in result]



if __name__ == "__main__":
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    #todo 请添加
    uri = "..." # the uri of your neo4j instance
    user = "..." # the username you set 
    password = "..." # the password you set
    
    app = App(uri, user, password)
    with open("./ner_output/entities.json","r") as f:
        data = json.load(f)

    entity = {
        'name':"",
        'content':{}
    }

    for key, value in data.items():
        entity['name'] = key
        entity['content'] = value
        app.create_node(entity)

    app.close()