"""CLI: python -m src.train --download --stage 'After semester 1'."""
import argparse
from .ml import STAGES, load_data, save_bundle, train_and_evaluate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/students.csv")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--stage", choices=list(STAGES), default="After semester 1")
    parser.add_argument("--tune", action="store_true")
    parser.add_argument("--full-benchmark", action="store_true", help="Evaluate seven classifier families")
    parser.add_argument("--no-calibration", action="store_true", help="Use uncalibrated baseline probabilities")
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    df = load_data(args.data, download=args.download)
    model, metrics = train_and_evaluate(df, args.stage, tune=args.tune,
                                        full_benchmark=args.full_benchmark,
                                        calibrate=not args.no_calibration)
    save_bundle(model, metrics, args.output)
    print(f"Saved to {args.output}; model={metrics['selected_model']}; test macro-F1={metrics['macro_f1']:.3f}")


if __name__ == "__main__":
    main()
