"use client";

import { useState } from "react";
import { Button } from "@nextui-org/button";
import { useDisclosure } from "@nextui-org/react";
import {
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
} from "@nextui-org/modal";

export default function Home() {
  const [url, setUrl] = useState("");
  const [prediction, setPrediction] = useState("");
  const [probability, setProbability] = useState(-1);

  const faqs = [
    {
      question: "Étape 1",
      answer:
        "Téléchargez l'extension depuis le bouton télécharger l'extension",
    },
    {
      question: "Étape 2",
      answer: "Lancer google chrome et ouvrir la page chrome://extensions/",
    },
    {
      question: "Étape 3",
      answer: "Cliquer sur le mode développeur en haut à droite",
    },
    {
      question: "Étape 4",
      answer:
        "Cliquer sur charger l'extension non empaquetée et sélectionner le dossier de l'extension",
    },
    {
      question: "Étape 5",
      answer: "L'extension est maintenant installée et prête à être utilisée",
    },
  ];

  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const handlePredict = async () => {
    const response = await fetch(
      "https://mdetector-api.arnidb.easypanel.host/api/predict",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url }),
      },
    );

    if (!response.ok) {
      return;
    }

    const response_data = await response.json();

    setPrediction(response_data.prediction);
    setProbability(response_data.proba);
  };

  return (
    <>
      <div className="relative overflow-hidden">
        <div className="max-w-[85rem] mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-8xl uppercase font-black text-gray-800 dark:text-neutral-200">
              <span className="text-red-500">MDetector</span> pour une
              navigation web plus sécurisée
            </h1>

            <p className="my-3 text-gray-600 dark:text-neutral-400 mb-7">
              Ensemble pour une navigation web plus sécurisée
            </p>

            {prediction == "good" && (
              <div
                className="m-2 mb-2 bg-green-100 border border-green-200 text-sm text-green-800 rounded-lg p-4 dark:bg-green-800/10 dark:border-green-900 dark:text-green-500"
                role="alert"
              >
                <p className="font-bold">
                  Ce site est sécurisé à {probability}%
                </p>
              </div>
            )}

            {prediction == "malicious" && (
              <div
                className="m-2 mb-2 bg-red-100 border border-red-200 text-sm text-red-800 rounded-lg p-4 dark:bg-red-800/10 dark:border-red-900 dark:text-red-500"
                role="alert"
              >
                <p className="font-bold">
                  Ce site est malveillant à {probability}%
                </p>
              </div>
            )}

            <div className="flex justify-center mt-10">
              <Button color="danger" size="md" as={"a"} href="https://drive.google.com/file/d/1GZlvIFU5vc38mSXI4d6_rn56Y-QEtwEk/view?usp=sharing">
                Télécharger l&apos;extension
              </Button>
              <Button
                className="ml-4"
                color="danger"
                size="md"
                variant="bordered"
                onPress={onOpen}
              >
                Voir les étapes d&apos;installation
              </Button>
            </div>

            <Modal isOpen={isOpen} size={"xl"} onOpenChange={onOpenChange}>
              <ModalContent>
                {(onClose) => (
                  <>
                    <ModalHeader className="flex flex-col gap-1">
                      Guide d&apos;installation
                    </ModalHeader>
                    <ModalBody>
                      {faqs.map((faq, index) => (
                        <div key={index} className="mb-4">
                          <h3 className="text-lg font-semibold">
                            {faq.question}
                          </h3>
                          <p className="text-gray-600 dark:text-neutral-400">
                            {faq.answer}
                          </p>
                        </div>
                      ))}
                    </ModalBody>
                    <ModalFooter>
                      <Button color="danger" variant="light" onPress={onClose}>
                        Close
                      </Button>
                    </ModalFooter>
                  </>
                )}
              </ModalContent>
            </Modal>

            <div className="mt-12 sm:mt-12 mx-auto max-w-xl relative">
              <div className="relative z-10 flex space-x-3 p-3 bg-white border rounded-lg shadow-lg shadow-gray-100 dark:bg-neutral-900 dark:border-neutral-700 dark:shadow-gray-900/20">
                <div className="flex-[1_0_0%] ">
                  {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
                  <label className="block text-sm text-gray-700 font-medium dark:text-white">
                    <span className="sr-only">https://www.example.com</span>
                  </label>
                  <input
                    className="py-2.5 px-4 block w-full border-transparent rounded-lg focus:border-red-500 focus:ring-red-500 dark:bg-neutral-900 dark:border-transparent dark:text-neutral-400 dark:placeholder-neutral-500 dark:focus:ring-neutral-600"
                    id="hs-predict"
                    name="hs-search-article-1"
                    placeholder="https://www.example.com"
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                </div>
                <div className="flex-[0_0_auto] ">
                  <button
                    className="size-[46px] inline-flex justify-center items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:pointer-events-none"
                    onClick={handlePredict}
                  >
                    <svg
                      className="flex-shrink-0 size-5"
                      fill="none"
                      height="24"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      width="24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <circle cx="11" cy="11" r="8" />
                      <path d="m21 21-4.3-4.3" />
                    </svg>
                  </button>
                </div>
              </div>

              <div className="hidden md:block absolute top-0 end-0 -translate-y-12 translate-x-20">
                <svg
                  className="w-16 h-auto text-red-500"
                  fill="none"
                  height="135"
                  viewBox="0 0 121 135"
                  width="121"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M5 16.4754C11.7688 27.4499 21.2452 57.3224 5 89.0164"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeWidth="10"
                  />
                  <path
                    d="M33.6761 112.104C44.6984 98.1239 74.2618 57.6776 83.4821 5"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeWidth="10"
                  />
                  <path
                    d="M50.5525 130C68.2064 127.495 110.731 117.541 116 78.0874"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeWidth="10"
                  />
                </svg>
              </div>

              <div className="hidden md:block absolute bottom-0 start-0 translate-y-10 -translate-x-32">
                <svg
                  className="w-40 h-auto text-purple-500"
                  fill="none"
                  height="188"
                  viewBox="0 0 347 188"
                  width="347"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M4 82.4591C54.7956 92.8751 30.9771 162.782 68.2065 181.385C112.642 203.59 127.943 78.57 122.161 25.5053C120.504 2.2376 93.4028 -8.11128 89.7468 25.5053C85.8633 61.2125 130.186 199.678 180.982 146.248L214.898 107.02C224.322 95.4118 242.9 79.2851 258.6 107.02C274.299 134.754 299.315 125.589 309.861 117.539L343 93.4426"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeWidth="7"
                  />
                  /{">"}
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
