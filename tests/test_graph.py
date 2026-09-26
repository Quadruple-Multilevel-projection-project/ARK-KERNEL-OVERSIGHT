import unittest
from ark01_cluster.graph import ARK01Graph

class TestARK01(unittest.TestCase):
    def test_registry_and_counts(self):
        g=ARK01Graph().build_scaffold()
        c=g.counts()
        self.assertEqual(c["gates"],321)
        self.assertEqual(c["canonical_unordered_pairs"],231)
        self.assertEqual(c["extension_slots"],90)
        self.assertEqual(c["root_slots"],32)
        self.assertEqual(c["relations_per_root"],31)
        self.assertEqual(c["endpoint_instances"],462) # 231 gates x two endpoints
        self.assertEqual(c["channel_nodes"],1848) # endpoints x four channels
        self.assertEqual(c["root_instances"],1848*32)
    def test_unresolved_does_not_propagate(self):
        g=ARK01Graph().build_scaffold()
        gate="G001"
        endpoint=g.edges[gate][0].target
        out=g.propagate({gate:1.0},steps=1)
        self.assertEqual(out[endpoint],1.0)
    def test_weight_validation(self):
        g=ARK01Graph().build_scaffold()
        with self.assertRaises(ValueError): g.add_edge("G001","G001",2)
if __name__=="__main__": unittest.main()
