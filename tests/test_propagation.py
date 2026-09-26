import unittest
from ark01_cluster.propagation import (
    Fragment, Letter, Root, LogicBook, LogicRule, Provenance,
    QueryPlan, PropagationEngine,
)

class PropagationTests(unittest.TestCase):
    def test_query_depth_and_verified_rule(self):
        src = Provenance('s1', 'p.1', True)
        letters = {'א': Letter('א', [Fragment('outer', 'outer', [
            Fragment('inner', 'seed', [Fragment('deep', 'deep-fact')])
        ])], ['r1'])}
        roots = {'r1': Root('r1', ['root-fact'], ['א'], [src])}
        rules = [LogicRule('rule1', 'logic-001', 'deep-fact', 'derived', src)]
        engine = PropagationEngine(letters, roots, {}, LogicBook({'logic-001':'L1'}), rules)
        shallow = engine.propagate(QueryPlan('q', 'cut', 1, ['logic-001'], ['א']))
        self.assertNotIn('derived', shallow.answer_fragments)
        deep = engine.propagate(QueryPlan('q', 'cut', 3, ['logic-001'], ['א']))
        self.assertIn('derived', deep.answer_fragments)

    def test_unverified_rule_does_not_fire_and_unknown_logic_is_reported(self):
        src = Provenance('s1', 'p.1', False)
        letter = Letter('א', [Fragment('f', 'seed')])
        rule = LogicRule('r', 'logic-001', 'seed', 'bad', src)
        engine = PropagationEngine({'א':letter}, {}, {}, LogicBook(), [rule])
        result = engine.propagate(QueryPlan('q','cut',1,['logic-001'],['א']))
        self.assertNotIn('bad', result.answer_fragments)
        self.assertTrue(any('no source-verified' in x for x in result.unresolved))

if __name__ == '__main__':
    unittest.main()
