import os
import unittest

import numpy as np

from src.db.Storage import Storage
from src.db.dbmanager import STORAGE_PATH, save_new_ml_agent, available_ml_agents, update_ml_agent, load_ml_agent, \
    remove_ml_agent


def reset_storage():
    if os.path.exists(STORAGE_PATH):
        os.remove(STORAGE_PATH)


class MyTestCase(unittest.TestCase):

    # test Storage
    def test_create_storage(self):
        reset_storage()

        sentinel = True
        msg = str()
        if os.path.exists(STORAGE_PATH):
            os.remove(STORAGE_PATH)
        try:
            storage = Storage(STORAGE_PATH)
        except Exception as e:
            sentinel = False
            msg = "Failed during initialization"
        else:
            sentinel &= os.path.exists(STORAGE_PATH)
        self.assertTrue(sentinel, msg)

    def test_read_write_storage(self):
        reset_storage()

        dummy_stored = {'a': 128, 'b': "abcd", 'c': ['a', 10, (1, 3, 2)]}
        storage = Storage(STORAGE_PATH)
        storage['a'] = 128
        storage['b'] = "abcd"
        storage['c'] = ['a', 10, (1, 3, 2)]
        test = {'a': storage['a'], 'b': storage['b'], 'c': storage['c']}
        self.assertDictEqual(test, dummy_stored)

    def test_keys_storage(self):
        reset_storage()

        k = ('a', 'b')
        storage = Storage(STORAGE_PATH)
        storage['a'] = np.random.uniform(-np.sqrt(6 / (20)), np.sqrt(6 / (20)), (10, 10))
        storage['b'] = np.random.uniform(-np.sqrt(6 / (24)), np.sqrt(6 / (24)), (12, 12))
        self.assertTupleEqual(storage.keys(), k)

    def test_del_attr(self):
        reset_storage()

        dummy_stored = {'a': 128, 'c': ['a', 10, (1, 3, 2)]}
        storage = Storage(STORAGE_PATH)
        storage['a'] = 128
        storage['b'] = "abcd"
        storage['c'] = ['a', 10, (1, 3, 2)]
        del storage['b']
        test = dict()
        for k in storage.keys():
            test[k] = storage[k]
        self.assertDictEqual(test, dummy_stored)

    # test dbmanager

    def test_save_new_agent(self):
        reset_storage()

        network_name = "test-net"
        network = [[1, 2, 3], [3]]
        ls = "strategy"
        act_f = "act_f"

        save_new_ml_agent(network_name, network, act_f, ls)

        buf = Storage(STORAGE_PATH)[network_name]
        self.assertDictEqual(buf, {"network": network, "ls": ls, "act_f": act_f})

    def test_available_ml_agents(self):
        reset_storage()

        agent_names = ["protocol-1", "ia_20_50_trained_10k", "agent_test_2"]
        db = Storage(STORAGE_PATH)
        for n in agent_names:
            db[n] = None

        self.assertSetEqual(set(available_ml_agents()), set(agent_names))

    def test_update_ml_agent(self):
        reset_storage()

        network_name = "test-agent"
        nn_old = [[0, 0, 0], [0, 0, 0]]
        nn_new = [[0.1, 0.2, 0.05], [0.2, 0.6, 0.12]]
        ls = "strat"
        lamb = None
        act_f = "activator"
        db = Storage(STORAGE_PATH)
        db[network_name] = {"network": nn_old, "ls": ls, "lamb": lamb, "act_f": act_f}
        update_ml_agent(network_name, nn_new)
        self.assertEqual(db[network_name]["network"], nn_new)

    def test_load_ml_agent(self):
        reset_storage()

        network_name = "test-agent"
        network = [[0, 0, 0], [0, 0, 0]]
        ls = "strat"
        act_f = "activator"
        db = Storage(STORAGE_PATH)
        db[network_name] = {"network": network, "ls": ls, "act_f": act_f}
        self.assertEqual(load_ml_agent(network_name), (network, act_f, ls))

    def test_remove_ml_agent(self):
        reset_storage()

        agent_names = ["protocol-1", "ia_20_50_trained_10k", "agent_test_2"]
        db = Storage(STORAGE_PATH)
        for n in agent_names:
            db[n] = None
        remove_ml_agent("protocol-1")
        remove_ml_agent("protocol-1")
        del agent_names[0]

        self.assertSetEqual(set(n for n in db.keys()), set(agent_names))


if __name__ == '__main__':
    unittest.main()
