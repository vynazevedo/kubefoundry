package main

import "testing"

func TestOwnershipBoundary(t *testing.T) {
	for _, tc := range []struct {
		meta object
		want bool
	}{
		{object{}, false},
		{object{"ownerReferences": []any{object{"uid": "other", "controller": true}}}, false},
		{object{"ownerReferences": []any{object{"uid": "ours", "controller": false}}}, false},
		{object{"ownerReferences": []any{object{"uid": "ours", "controller": true}}}, true},
	} {
		if owned(tc.meta, "ours") != tc.want {
			t.Fatalf("unexpected ownership for %#v", tc.meta)
		}
	}
}
