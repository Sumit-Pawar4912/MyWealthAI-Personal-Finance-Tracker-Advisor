#!/usr/bin/env python
"""
Train ML Models for MyWelthAI
Run this script to train and save all ML models
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_model_trainer import MLModelTrainer

if __name__ == '__main__':
    print("\n📊 MyWelthAI ML Model Training")
    print("================================\n")
    
    # Initialize trainer
    trainer = MLModelTrainer(model_dir='models')
    
    # Train all models
    success = trainer.train_all_models()
    
    if success:
        print("\n✅ Models ready for backend!")
        print("Start backend with: python run.py")
    else:
        print("\n❌ Training failed. Check errors above.")
        sys.exit(1)
