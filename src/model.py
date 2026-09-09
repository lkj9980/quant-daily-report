def generate_signals(model, X_test, confidence_threshold=0.70):
    # 확률 분포 출력 [하락 확률, 횡보 확률, 상승 확률]
    probs = model.predict_proba(X_test)
    max_probs = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1) # 0: 하락, 1: 횡보, 2: 상승
    
    signals = []
    for pred, conf in zip(predictions, max_probs):
        if conf < confidence_threshold:
            signals.append("HOLD_CASH (No-Action Zone)")
        else:
            signals.append(["DOWN", "SIDEWAYS", "UP"][pred])
            
    return signals, max_probs
