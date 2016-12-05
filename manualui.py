import adage
import adage.nodestate as nodestate
import adage.dagstate as dagstate

class manualadage(object):
    def __init__(self,stateobject,backend):
        self.state = stateobject
        self.backend = backend

    def status(self):
        if adage.nodes_left_or_rule_applicable(self.state):
            return 'RUNNING'

        failed = any(self.state.dag.getNode(x).state == nodestate.FAILED for x in self.state.dag.nodes())
        return 'FAILED' if failed else 'SUCCESS'

    def applicable_rules(self):
        applicable = []
        for rule in reversed([x for x in self.state.rules]):
            if rule.applicable(self.state):
                applicable += [rule.identifier]
        return applicable

    def rule(self,ruleid):
        return [(i,x) for i,x in enumerate(self.state.rules) if x.identifier==ruleid][0]

    def apply_rule(self,ruleid):
        index = self.rule(ruleid)[0]
        rule  = self.state.rules.pop(index)
        rule.apply(self.state)
        self.state.applied_rules.append(rule)

    def submittable_nodes(self):
        nodes = []
        for nodeid in self.state.dag.nodes():
            nodeobj = self.state.dag.getNode(nodeid)
            if nodeobj.submit_time:
                continue;
            if dagstate.upstream_ok(self.state.dag,nodeobj):
                nodes += [nodeid]
        return nodes

    def submit_node(self,nodeid):
        nodeobj = self.state.dag.getNode(nodeid)
        adage.submit_node(nodeobj,self.backend)
